from pathlib import Path
import json
import subprocess
from typing import Optional

REMOTION_DIR = Path(__file__).parent.parent / "remotion"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def render_remotion_graphic(
    composition: str,
    props: dict,
    output_path: str,
) -> Path:
    """Render a single Remotion composition to MP4."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "npx", "remotion", "render",
            "src/index.ts",
            composition,
            str(output.absolute()),
            f"--props={json.dumps(props)}",
        ],
        cwd=str(REMOTION_DIR),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Remotion render failed for '{composition}':\n{result.stderr}"
        )

    return output


def case_to_props(case, channel_name: str = "Finally Solved", accent_color: str = "#c41e3a") -> dict:
    return {
        "caseName": case.name,
        "year": case.year,
        "channelName": channel_name,
        "microSeries": case.micro_series,
        "failureType": case.failure_type.replace("_", " ").title(),
        "complexity": case.complexity,
        "accentColor": accent_color,
    }


def render_case_graphics(
    case,
    slot: str,
    output_dir: Optional[Path] = None,
    channel_name: str = "Finally Solved",
    accent_color: str = "#c41e3a",
) -> dict[str, str]:
    """Render all Remotion graphics for a case+slot. Returns {name: path}."""
    if output_dir is None:
        output_dir = OUTPUT_DIR / case.id / slot / "graphics"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    props = case_to_props(case, channel_name, accent_color)
    rendered: dict[str, str] = {}

    # Episode intro
    intro_path = output_dir / "episode_intro.mp4"
    render_remotion_graphic(
        "EpisodeIntro",
        {**props, "episodeTitle": case.name, "subtitle": (case.summary or "")[:120]},
        str(intro_path),
    )
    rendered["episode_intro"] = str(intro_path)

    # Title card
    title_path = output_dir / "title_card.mp4"
    render_remotion_graphic("CaseTitleCard", props, str(title_path))
    rendered["title_card"] = str(title_path)

    # Data graphic
    data_path = output_dir / "data_graphic.mp4"
    render_remotion_graphic("DataGraphic", props, str(data_path))
    rendered["data_graphic"] = str(data_path)

    # Short hook for short-form slots
    if slot in ("mon_short", "wed_short", "thu_pi", "fri_short", "sat_pi"):
        hook_path = output_dir / "short_hook.mp4"
        hook_text = (case.summary or case.name)[:100]
        render_remotion_graphic(
            "ShortHook",
            {**props, "hookText": hook_text},
            str(hook_path),
        )
        rendered["short_hook"] = str(hook_path)

    return rendered


def assemble_episode(
    case_id: str,
    slot: str,
    output_dir: Optional[Path] = None,
) -> Path:
    """Assemble a final episode MP4 from voiceover + BGM + graphics + b-roll."""
    try:
        from moviepy import (
            AudioFileClip,
            ColorClip,
            CompositeAudioClip,
            VideoFileClip,
            concatenate_audioclips,
            concatenate_videoclips,
        )
    except ImportError:
        raise RuntimeError("moviepy is not installed. Run: pip install moviepy")

    if output_dir is None:
        output_dir = OUTPUT_DIR / case_id / slot
    output_dir = Path(output_dir)

    voiceover_path = output_dir / "voiceover.mp3"
    bgm_path = output_dir / "bgm.mp3"
    graphics_dir = output_dir / "graphics"
    broll_dir = output_dir / "broll"
    output_path = output_dir / "final.mp4"

    if not voiceover_path.exists():
        raise FileNotFoundError(
            f"Voiceover not found at {voiceover_path}\n"
            f"Expected layout:\n"
            f"  output/{case_id}/{slot}/voiceover.mp3  (required)\n"
            f"  output/{case_id}/{slot}/bgm.mp3        (optional)\n"
            f"  output/{case_id}/{slot}/broll/*.mp4    (optional)\n"
            f"  output/{case_id}/{slot}/graphics/*.mp4 (auto-rendered)"
        )

    voiceover = AudioFileClip(str(voiceover_path))
    total_duration = voiceover.duration

    # Audio mix
    audio_clips: list = [voiceover]
    if bgm_path.exists():
        bgm = AudioFileClip(str(bgm_path)).multiply_volume(0.12)
        if bgm.duration < total_duration:
            loops = int(total_duration / bgm.duration) + 1
            bgm = concatenate_audioclips([bgm] * loops).subclipped(0, total_duration)
        else:
            bgm = bgm.subclipped(0, total_duration)
        audio_clips.append(bgm)
    mixed_audio = CompositeAudioClip(audio_clips)

    # Video clips: graphics first, then b-roll
    video_clips = []
    if graphics_dir.exists():
        for f in sorted(graphics_dir.glob("*.mp4")):
            video_clips.append(VideoFileClip(str(f)))
    if broll_dir.exists():
        for f in sorted(broll_dir.glob("*.mp4")):
            video_clips.append(VideoFileClip(str(f)))

    if video_clips:
        raw_video = concatenate_videoclips(video_clips, method="compose")
        if raw_video.duration < total_duration:
            raw_video = raw_video.loop(duration=total_duration)
        else:
            raw_video = raw_video.subclipped(0, total_duration)
    else:
        raw_video = ColorClip(size=(1920, 1080), color=(8, 8, 16), duration=total_duration)

    final = raw_video.with_audio(mixed_audio)
    final.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None,
    )

    return output_path
