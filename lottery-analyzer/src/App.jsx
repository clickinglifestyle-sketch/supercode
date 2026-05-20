import { useState, useMemo, useRef } from 'react';
import { CheckCircle, XCircle, AlertCircle, Shuffle, Bookmark, BarChart2, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

const PRIZES = [250000, 500, 50, 10, 2, 0, 0, 0, 2, 10, 50, 500, 250000];

const lotteryData = [
  { date: "Wed May 06, 2026", numbers: [4,5,8,9,11,12,14,16,17,19,20,23] },
  { date: "Tue May 05, 2026", numbers: [1,3,5,6,7,9,11,12,15,16,23,24] },
  { date: "Mon May 04, 2026", numbers: [1,5,6,8,9,10,12,13,15,19,23,24] },
  { date: "Sat May 02, 2026", numbers: [1,4,7,8,10,11,13,17,18,19,22,24] },
  { date: "Fri May 01, 2026", numbers: [3,7,9,10,11,12,13,16,19,21,23,24] },
  { date: "Thu Apr 30, 2026", numbers: [1,2,3,5,7,13,14,16,19,21,22,24] },
  { date: "Wed Apr 29, 2026", numbers: [5,8,10,11,12,15,16,17,19,20,23,24] },
  { date: "Tue Apr 28, 2026", numbers: [5,6,7,11,12,13,15,17,18,20,21,24] },
  { date: "Mon Apr 27, 2026", numbers: [2,3,4,5,8,11,17,18,19,21,22,23] },
  { date: "Sat Apr 25, 2026", numbers: [1,3,7,8,9,11,15,18,19,20,21,24] },
  { date: "Fri Apr 24, 2026", numbers: [1,4,5,6,7,10,13,15,18,21,22,24] },
  { date: "Thu Apr 23, 2026", numbers: [2,4,5,6,7,9,10,13,14,16,18,20] },
  { date: "Wed Apr 22, 2026", numbers: [1,3,4,6,11,13,14,19,21,22,23,24] },
  { date: "Tue Apr 21, 2026", numbers: [3,4,5,6,9,11,12,13,15,16,19,22] },
  { date: "Mon Apr 20, 2026", numbers: [1,3,4,5,6,7,9,10,11,12,16,23] },
  { date: "Sat Apr 18, 2026", numbers: [1,2,3,4,8,11,12,13,14,15,21,24] },
  { date: "Fri Apr 17, 2026", numbers: [1,2,3,4,9,14,15,17,19,22,23,24] },
  { date: "Thu Apr 16, 2026", numbers: [4,5,6,8,9,11,12,13,14,20,21,23] },
  { date: "Wed Apr 15, 2026", numbers: [2,5,6,8,9,12,14,15,18,20,21,24] },
  { date: "Tue Apr 14, 2026", numbers: [2,3,4,7,8,9,11,14,15,17,21,24] },
  { date: "Mon Apr 13, 2026", numbers: [1,5,6,7,8,12,16,17,20,22,23,24] },
  { date: "Sat Apr 11, 2026", numbers: [3,4,5,6,7,9,10,13,15,20,22,23] },
  { date: "Fri Apr 10, 2026", numbers: [1,2,3,7,8,10,11,12,14,16,23,24] },
  { date: "Thu Apr 09, 2026", numbers: [2,4,6,7,10,13,16,18,19,20,23,24] },
  { date: "Wed Apr 08, 2026", numbers: [2,3,4,6,8,10,12,17,18,19,22,24] },
  { date: "Tue Apr 07, 2026", numbers: [2,3,5,7,9,11,12,14,19,20,21,22] },
  { date: "Mon Apr 06, 2026", numbers: [1,2,3,5,6,8,9,10,15,18,20,21] },
  { date: "Sat Apr 04, 2026", numbers: [3,4,6,7,8,9,15,16,19,22,23,24] },
  { date: "Fri Apr 03, 2026", numbers: [2,3,4,6,8,9,10,13,21,22,23,24] },
  { date: "Thu Apr 02, 2026", numbers: [3,4,5,7,9,13,14,15,16,17,23,24] },
  { date: "Wed Apr 01, 2026", numbers: [2,4,5,11,13,14,16,17,18,19,22,23] },
  { date: "Tue Mar 31, 2026", numbers: [1,3,4,7,9,10,12,13,17,19,21,24] },
  { date: "Mon Mar 30, 2026", numbers: [3,6,7,10,11,14,15,16,19,20,22,24] },
  { date: "Sat Mar 28, 2026", numbers: [1,6,7,8,9,11,12,14,16,20,23,24] },
  { date: "Fri Mar 27, 2026", numbers: [1,2,5,6,7,12,13,14,17,18,20,21] },
  { date: "Thu Mar 26, 2026", numbers: [3,4,5,8,9,11,13,18,21,22,23,24] },
  { date: "Wed Mar 25, 2026", numbers: [2,3,4,5,6,10,13,14,17,20,22,23] },
  { date: "Tue Mar 24, 2026", numbers: [1,2,5,7,9,10,12,13,16,18,19,21] },
  { date: "Mon Mar 23, 2026", numbers: [1,2,4,8,10,11,12,13,18,19,23,24] },
  { date: "Sat Mar 21, 2026", numbers: [4,5,6,7,8,11,14,15,16,17,18,24] },
  { date: "Fri Mar 20, 2026", numbers: [1,6,10,12,13,14,15,17,19,21,23,24] },
  { date: "Thu Mar 19, 2026", numbers: [1,2,3,6,9,10,12,15,18,21,22,24] },
  { date: "Wed Mar 18, 2026", numbers: [4,6,7,10,11,12,13,14,18,20,21,23] },
  { date: "Tue Mar 17, 2026", numbers: [2,3,4,5,7,9,12,14,15,19,20,22] },
  { date: "Mon Mar 16, 2026", numbers: [1,4,5,6,8,9,12,16,18,19,21,22] },
  { date: "Sat Mar 14, 2026", numbers: [2,7,8,10,11,12,13,15,16,18,20,24] },
  { date: "Fri Mar 13, 2026", numbers: [1,4,6,8,9,10,11,13,18,19,21,22] },
  { date: "Thu Mar 12, 2026", numbers: [3,4,7,9,10,12,14,16,17,22,23,24] },
  { date: "Wed Mar 11, 2026", numbers: [1,3,6,7,8,10,11,14,15,16,19,20] },
  { date: "Tue Mar 10, 2026", numbers: [3,4,6,7,9,12,13,14,18,20,23,24] },
  { date: "Mon Mar 09, 2026", numbers: [2,4,6,8,9,10,14,15,16,17,19,23] },
  { date: "Sat Mar 07, 2026", numbers: [3,5,6,7,10,14,15,17,18,19,21,22] },
  { date: "Fri Mar 06, 2026", numbers: [1,2,3,7,9,10,13,14,16,18,21,22] },
  { date: "Thu Mar 05, 2026", numbers: [1,8,10,12,13,14,15,16,17,19,22,23] },
  { date: "Wed Mar 04, 2026", numbers: [1,4,6,7,9,10,17,20,21,22,23,24] },
  { date: "Tue Mar 03, 2026", numbers: [1,2,5,6,7,8,10,11,12,14,15,17] },
  { date: "Mon Mar 02, 2026", numbers: [1,2,3,5,9,10,12,14,16,21,22,24] },
  { date: "Sat Feb 28, 2026", numbers: [2,3,4,7,8,9,11,12,17,19,21,23] },
  { date: "Fri Feb 27, 2026", numbers: [1,2,6,8,9,10,13,18,19,21,22,23] },
  { date: "Thu Feb 26, 2026", numbers: [1,5,7,9,11,12,13,17,18,20,21,22] },
  { date: "Wed Feb 25, 2026", numbers: [1,2,5,6,7,11,12,13,18,20,21,23] },
  { date: "Tue Feb 24, 2026", numbers: [1,4,5,6,7,10,12,13,18,19,20,23] },
  { date: "Mon Feb 23, 2026", numbers: [3,4,6,9,12,13,14,16,21,22,23,24] },
  { date: "Sat Feb 21, 2026", numbers: [1,5,6,8,9,12,13,14,15,16,20,21] },
  { date: "Fri Feb 20, 2026", numbers: [1,2,3,6,7,10,11,14,17,19,21,24] },
  { date: "Thu Feb 19, 2026", numbers: [2,7,8,10,11,14,18,19,20,21,22,23] },
  { date: "Wed Feb 18, 2026", numbers: [2,3,5,7,8,10,13,14,19,21,23,24] },
  { date: "Tue Feb 17, 2026", numbers: [4,5,6,7,10,13,14,19,21,22,23,24] },
  { date: "Mon Feb 16, 2026", numbers: [1,4,7,8,9,10,11,18,19,20,23,24] },
  { date: "Sat Feb 14, 2026", numbers: [1,3,4,5,7,12,14,15,16,17,18,24] },
  { date: "Fri Feb 13, 2026", numbers: [4,5,6,8,9,11,13,15,16,17,18,21] },
  { date: "Thu Feb 12, 2026", numbers: [1,2,5,8,9,11,16,17,18,19,23,24] },
  { date: "Wed Feb 11, 2026", numbers: [1,2,6,8,9,11,15,17,19,21,22,24] },
  { date: "Tue Feb 10, 2026", numbers: [1,2,4,5,6,9,14,15,18,19,23,24] },
  { date: "Mon Feb 09, 2026", numbers: [1,3,6,8,12,13,14,15,16,17,23,24] },
  { date: "Sat Feb 07, 2026", numbers: [5,11,12,13,14,15,16,18,19,21,22,23] },
  { date: "Fri Feb 06, 2026", numbers: [1,3,5,6,7,8,9,13,15,16,22,24] },
  { date: "Thu Feb 05, 2026", numbers: [1,3,5,7,10,11,12,18,19,20,21,22] },
  { date: "Wed Feb 04, 2026", numbers: [1,2,5,7,8,12,13,16,17,18,19,23] },
  { date: "Tue Feb 03, 2026", numbers: [1,3,8,9,11,13,16,17,18,20,22,23] },
  { date: "Mon Feb 02, 2026", numbers: [3,6,7,8,9,10,11,14,15,16,22,23] },
  { date: "Sat Jan 31, 2026", numbers: [3,4,6,7,8,11,14,15,16,21,23,24] },
  { date: "Fri Jan 30, 2026", numbers: [3,4,6,9,12,15,16,18,20,21,22,24] },
  { date: "Thu Jan 29, 2026", numbers: [1,4,5,6,8,9,10,12,13,15,20,23] },
  { date: "Wed Jan 28, 2026", numbers: [1,2,4,7,8,9,13,16,18,20,22,24] },
  { date: "Tue Jan 27, 2026", numbers: [1,2,4,5,6,7,9,10,16,17,18,21] },
  { date: "Mon Jan 26, 2026", numbers: [1,2,4,5,6,9,12,14,16,20,22,24] },
  { date: "Sat Jan 24, 2026", numbers: [1,2,3,5,7,9,13,15,17,19,20,24] },
  { date: "Fri Jan 23, 2026", numbers: [1,2,4,5,8,10,14,16,17,19,21,24] },
  { date: "Thu Jan 22, 2026", numbers: [1,2,3,4,7,8,10,11,13,14,18,19] },
  { date: "Wed Jan 21, 2026", numbers: [3,4,5,6,7,8,10,13,16,18,21,22] },
  { date: "Tue Jan 20, 2026", numbers: [2,4,5,10,12,13,14,15,16,19,22,24] },
  { date: "Mon Jan 19, 2026", numbers: [3,4,5,8,10,12,14,17,20,21,22,23] },
  { date: "Sat Jan 17, 2026", numbers: [2,3,4,5,6,9,12,14,17,19,20,21] },
  { date: "Fri Jan 16, 2026", numbers: [1,3,7,8,10,12,14,15,18,19,21,23] },
  { date: "Thu Jan 15, 2026", numbers: [1,3,6,7,10,12,16,17,18,19,21,22] },
  { date: "Wed Jan 14, 2026", numbers: [2,3,5,6,9,10,11,12,13,18,23,24] },
  { date: "Tue Jan 13, 2026", numbers: [2,4,5,7,8,13,15,16,18,21,22,23] },
  { date: "Mon Jan 12, 2026", numbers: [1,2,8,9,12,13,14,15,18,21,22,23] },
  { date: "Sat Jan 10, 2026", numbers: [1,3,5,6,9,10,12,13,15,16,19,21] },
  { date: "Fri Jan 09, 2026", numbers: [5,9,12,13,14,15,16,19,20,21,22,24] },
  { date: "Thu Jan 08, 2026", numbers: [1,2,4,6,7,8,12,15,19,21,22,24] },
  { date: "Wed Jan 07, 2026", numbers: [1,3,4,6,10,13,19,20,21,22,23,24] },
  { date: "Tue Jan 06, 2026", numbers: [3,8,10,11,12,13,14,15,16,17,20,24] },
  { date: "Mon Jan 05, 2026", numbers: [1,3,4,8,11,12,15,17,18,19,21,22] },
  { date: "Sat Jan 03, 2026", numbers: [2,4,5,7,9,11,13,15,17,18,19,24] },
  { date: "Fri Jan 02, 2026", numbers: [1,2,4,5,6,14,15,18,20,21,22,23] },
  { date: "Thu Jan 01, 2026", numbers: [2,4,6,8,11,13,15,16,17,18,19,24] },
  { date: "Wed Dec 31, 2025", numbers: [1,2,4,5,7,9,10,11,13,14,16,24] },
  { date: "Tue Dec 30, 2025", numbers: [2,3,4,6,7,10,12,14,16,17,19,21] },
  { date: "Mon Dec 29, 2025", numbers: [5,6,8,9,12,13,14,16,18,19,22,24] },
  { date: "Sat Dec 27, 2025", numbers: [1,3,4,7,8,9,11,12,14,17,21,24] },
  { date: "Fri Dec 26, 2025", numbers: [2,5,7,8,9,11,13,14,15,18,20,24] },
  { date: "Thu Dec 25, 2025", numbers: [1,2,3,6,8,11,13,15,17,20,22,23] },
  { date: "Wed Dec 24, 2025", numbers: [1,2,6,9,15,16,17,18,19,20,23,24] },
  { date: "Tue Dec 23, 2025", numbers: [1,3,4,5,6,8,9,10,16,21,22,23] },
  { date: "Mon Dec 22, 2025", numbers: [2,3,6,7,8,10,11,17,18,20,22,24] },
  { date: "Sat Dec 20, 2025", numbers: [2,5,7,8,9,13,14,17,18,20,21,23] },
  { date: "Fri Dec 19, 2025", numbers: [2,3,6,7,12,13,14,15,16,17,19,21] },
  { date: "Thu Dec 18, 2025", numbers: [3,4,7,10,13,14,15,16,19,20,22,24] },
  { date: "Wed Dec 17, 2025", numbers: [1,2,5,8,9,11,16,18,21,22,23,24] },
  { date: "Tue Dec 16, 2025", numbers: [1,2,3,5,8,12,16,18,19,20,21,24] },
  { date: "Mon Dec 15, 2025", numbers: [1,2,7,9,10,11,12,15,18,21,23,24] },
  { date: "Sat Dec 13, 2025", numbers: [2,3,4,6,7,8,9,10,17,18,20,22] },
  { date: "Fri Dec 12, 2025", numbers: [1,2,3,5,6,10,12,19,20,21,22,24] },
  { date: "Thu Dec 11, 2025", numbers: [2,3,5,6,11,12,17,18,19,21,22,23] },
  { date: "Wed Dec 10, 2025", numbers: [1,2,4,6,11,12,13,17,19,20,21,22] },
  { date: "Tue Dec 09, 2025", numbers: [1,3,4,6,8,12,14,15,17,20,21,24] },
  { date: "Mon Dec 08, 2025", numbers: [4,5,7,10,11,12,13,16,17,18,23,24] },
  { date: "Sat Dec 06, 2025", numbers: [1,5,11,12,13,14,15,17,19,20,21,24] },
  { date: "Fri Dec 05, 2025", numbers: [6,7,9,10,11,12,15,16,17,18,19,24] },
  { date: "Thu Dec 04, 2025", numbers: [3,4,5,6,8,10,12,14,15,17,19,20] },
  { date: "Wed Dec 03, 2025", numbers: [5,6,7,9,13,14,15,16,17,18,20,22] },
  { date: "Tue Dec 02, 2025", numbers: [2,3,5,7,9,11,12,13,14,16,22,24] },
  { date: "Mon Dec 01, 2025", numbers: [2,3,4,5,7,8,12,14,15,18,20,21] },
  { date: "Sat Nov 29, 2025", numbers: [2,3,4,5,7,11,13,18,19,21,23,24] },
  { date: "Fri Nov 28, 2025", numbers: [2,3,4,5,7,11,12,13,15,16,17,18] },
  { date: "Thu Nov 27, 2025", numbers: [4,5,6,7,9,14,15,19,20,21,23,24] },
  { date: "Wed Nov 26, 2025", numbers: [1,4,5,6,8,10,12,13,14,15,19,22] },
  { date: "Tue Nov 25, 2025", numbers: [1,3,8,10,12,13,15,17,18,20,21,22] },
  { date: "Mon Nov 24, 2025", numbers: [1,2,4,8,9,10,12,16,17,22,23,24] },
  { date: "Sat Nov 22, 2025", numbers: [2,4,5,8,9,12,14,16,18,20,22,23] },
  { date: "Fri Nov 21, 2025", numbers: [3,4,6,7,10,12,13,14,17,19,22,24] },
  { date: "Thu Nov 20, 2025", numbers: [1,2,3,8,9,10,12,15,16,17,18,24] },
  { date: "Wed Nov 19, 2025", numbers: [3,5,6,7,9,10,11,13,14,20,22,24] },
  { date: "Tue Nov 18, 2025", numbers: [1,2,3,4,5,10,13,17,18,20,22,24] },
  { date: "Mon Nov 17, 2025", numbers: [1,2,3,4,5,7,11,12,13,17,19,20] },
  { date: "Sat Nov 15, 2025", numbers: [1,5,6,7,8,11,13,15,16,19,22,23] },
  { date: "Fri Nov 14, 2025", numbers: [2,5,6,9,10,13,16,18,20,21,22,24] },
  { date: "Thu Nov 13, 2025", numbers: [1,2,5,6,9,12,13,14,15,18,19,21] },
  { date: "Wed Nov 12, 2025", numbers: [2,3,5,7,10,11,12,16,20,22,23,24] },
  { date: "Tue Nov 11, 2025", numbers: [1,2,4,5,7,9,15,16,17,19,23,24] },
  { date: "Mon Nov 10, 2025", numbers: [1,2,4,5,6,8,10,11,16,19,20,24] },
  { date: "Sat Nov 08, 2025", numbers: [1,5,8,11,13,14,15,16,17,18,23,24] },
  { date: "Fri Nov 07, 2025", numbers: [2,4,6,9,12,13,14,15,20,21,22,24] },
  { date: "Thu Nov 06, 2025", numbers: [1,2,5,7,10,11,12,17,18,19,21,24] },
  { date: "Wed Nov 05, 2025", numbers: [1,5,7,8,10,11,13,14,15,18,19,22] },
  { date: "Tue Nov 04, 2025", numbers: [1,2,3,4,9,11,12,13,15,16,20,21] },
  { date: "Mon Nov 03, 2025", numbers: [1,3,5,7,9,12,14,16,19,20,21,23] },
  { date: "Sat Nov 01, 2025", numbers: [1,4,6,8,9,11,14,17,18,20,22,24] },
  { date: "Fri Oct 31, 2025", numbers: [1,2,6,8,9,11,12,13,14,15,17,21] },
  { date: "Thu Oct 30, 2025", numbers: [5,7,9,12,13,14,16,17,18,19,20,23] },
  { date: "Wed Oct 29, 2025", numbers: [2,4,5,7,8,10,11,12,13,22,23,24] },
  { date: "Tue Oct 28, 2025", numbers: [3,5,6,9,10,11,14,15,16,17,22,24] },
  { date: "Mon Oct 27, 2025", numbers: [1,2,3,8,10,17,18,19,20,22,23,24] },
  { date: "Sat Oct 25, 2025", numbers: [1,2,4,9,10,14,19,20,21,22,23,24] },
  { date: "Fri Oct 24, 2025", numbers: [2,3,10,11,12,17,18,19,20,21,22,24] },
  { date: "Thu Oct 23, 2025", numbers: [1,2,4,10,11,12,13,14,16,20,21,24] },
  { date: "Wed Oct 22, 2025", numbers: [1,2,3,7,10,11,13,17,18,19,21,22] },
  { date: "Tue Oct 21, 2025", numbers: [1,3,7,10,11,12,13,14,18,19,22,24] },
  { date: "Mon Oct 20, 2025", numbers: [2,6,9,10,11,12,13,15,21,22,23,24] },
  { date: "Sat Oct 18, 2025", numbers: [3,8,9,11,12,13,14,17,18,20,21,23] },
  { date: "Fri Oct 17, 2025", numbers: [3,4,6,9,11,12,17,18,20,21,22,24] },
  { date: "Thu Oct 16, 2025", numbers: [1,2,3,4,5,6,9,12,14,17,22,23] },
  { date: "Wed Oct 15, 2025", numbers: [1,2,4,7,10,13,14,17,18,20,22,24] },
  { date: "Tue Oct 14, 2025", numbers: [2,4,5,6,7,13,15,17,18,19,22,23] },
  { date: "Mon Oct 13, 2025", numbers: [3,6,10,11,12,14,16,17,20,21,23,24] },
  { date: "Sat Oct 11, 2025", numbers: [2,5,6,8,10,11,15,19,20,21,22,23] },
  { date: "Fri Oct 10, 2025", numbers: [4,6,7,8,9,11,12,16,20,21,22,23] },
  { date: "Thu Oct 09, 2025", numbers: [3,5,6,7,9,16,17,19,21,22,23,24] },
  { date: "Wed Oct 08, 2025", numbers: [2,6,7,8,9,11,12,15,20,21,23,24] },
  { date: "Tue Oct 07, 2025", numbers: [1,3,4,5,8,10,11,14,15,16,18,24] },
  { date: "Mon Oct 06, 2025", numbers: [3,4,6,7,9,10,12,14,15,20,22,23] },
  { date: "Sat Oct 04, 2025", numbers: [3,6,7,8,9,14,15,16,19,21,22,24] },
  { date: "Fri Oct 03, 2025", numbers: [3,4,6,7,8,10,11,12,13,15,21,23] },
  { date: "Thu Oct 02, 2025", numbers: [2,3,4,5,6,7,11,12,14,17,23,24] },
  { date: "Wed Oct 01, 2025", numbers: [1,2,5,7,10,12,13,15,20,21,22,24] },
  { date: "Tue Sep 30, 2025", numbers: [3,6,8,9,10,11,13,15,16,19,20,22] },
  { date: "Mon Sep 29, 2025", numbers: [1,7,8,10,11,12,13,14,19,20,22,23] },
  { date: "Sat Sep 27, 2025", numbers: [5,6,7,10,12,15,16,17,20,22,23,24] },
  { date: "Fri Sep 26, 2025", numbers: [3,5,6,8,9,11,12,13,15,16,21,22] },
  { date: "Thu Sep 25, 2025", numbers: [4,5,6,9,10,11,12,14,16,17,19,24] },
  { date: "Wed Sep 24, 2025", numbers: [2,5,6,7,8,9,10,11,12,21,22,23] },
  { date: "Tue Sep 23, 2025", numbers: [1,2,3,7,8,9,12,18,19,20,21,23] },
  { date: "Mon Sep 22, 2025", numbers: [2,4,6,7,9,10,11,15,17,18,21,23] },
  { date: "Sat Sep 20, 2025", numbers: [1,2,8,9,10,11,14,15,16,18,23,24] },
  { date: "Fri Sep 19, 2025", numbers: [2,8,9,10,12,14,15,16,17,19,21,23] },
  { date: "Thu Sep 18, 2025", numbers: [1,4,5,7,8,10,12,13,15,18,22,23] },
  { date: "Wed Sep 17, 2025", numbers: [3,4,5,6,10,12,13,16,18,19,20,22] },
  { date: "Tue Sep 16, 2025", numbers: [6,9,10,11,12,13,14,15,18,19,21,22] },
  { date: "Mon Sep 15, 2025", numbers: [1,3,5,6,8,9,11,12,18,19,21,22] },
  { date: "Sat Sep 13, 2025", numbers: [1,2,3,4,5,8,11,15,17,19,20,22] },
  { date: "Fri Sep 12, 2025", numbers: [1,4,6,8,10,11,15,16,18,21,23,24] },
  { date: "Thu Sep 11, 2025", numbers: [2,3,4,6,8,9,12,14,16,17,19,20] },
  { date: "Wed Sep 10, 2025", numbers: [1,2,3,5,7,9,11,14,15,17,18,21] },
  { date: "Tue Sep 09, 2025", numbers: [1,3,6,8,12,13,14,16,17,18,23,24] },
  { date: "Mon Sep 08, 2025", numbers: [2,3,4,5,6,13,14,15,16,17,18,20] },
  { date: "Sat Sep 06, 2025", numbers: [3,8,10,13,16,17,18,19,20,22,23,24] },
  { date: "Fri Sep 05, 2025", numbers: [1,2,3,5,7,9,12,14,15,18,21,23] },
  { date: "Thu Sep 04, 2025", numbers: [1,2,4,8,9,10,11,13,14,15,16,20] },
  { date: "Wed Sep 03, 2025", numbers: [2,7,8,9,10,11,14,17,18,21,22,24] },
  { date: "Tue Sep 02, 2025", numbers: [5,9,10,11,14,16,17,18,20,21,22,23] },
  { date: "Mon Sep 01, 2025", numbers: [1,5,6,7,9,10,11,12,13,17,19,21] },
  { date: "Sat Aug 30, 2025", numbers: [4,6,8,10,12,15,16,17,18,19,20,22] },
  { date: "Fri Aug 29, 2025", numbers: [2,3,4,8,10,12,13,14,15,18,19,21] },
  { date: "Thu Aug 28, 2025", numbers: [1,2,4,8,10,11,14,15,18,19,20,23] },
  { date: "Wed Aug 27, 2025", numbers: [3,4,6,7,8,9,12,14,15,18,21,23] },
  { date: "Tue Aug 26, 2025", numbers: [3,5,6,7,12,13,14,15,19,20,21,24] },
  { date: "Mon Aug 25, 2025", numbers: [1,3,8,9,10,11,16,18,20,21,23,24] },
  { date: "Sat Aug 23, 2025", numbers: [4,5,6,7,10,13,14,15,18,19,20,22] },
  { date: "Fri Aug 22, 2025", numbers: [3,4,5,6,7,8,16,18,19,20,21,24] },
  { date: "Thu Aug 21, 2025", numbers: [2,4,5,6,7,11,12,13,14,15,17,23] },
  { date: "Wed Aug 20, 2025", numbers: [2,7,8,11,12,14,16,19,20,21,22,24] },
  { date: "Tue Aug 19, 2025", numbers: [3,5,9,12,14,15,17,18,20,22,23,24] },
  { date: "Mon Aug 18, 2025", numbers: [2,3,4,5,6,7,9,13,15,16,17,18] },
  { date: "Sat Aug 16, 2025", numbers: [3,4,8,9,10,12,16,17,20,22,23,24] },
  { date: "Fri Aug 15, 2025", numbers: [3,9,12,15,16,18,19,20,21,22,23,24] },
  { date: "Thu Aug 14, 2025", numbers: [3,4,5,8,9,12,13,14,20,21,23,24] },
  { date: "Wed Aug 13, 2025", numbers: [2,3,7,10,12,13,15,19,20,21,22,23] },
  { date: "Tue Aug 12, 2025", numbers: [2,3,6,15,16,18,19,20,21,22,23,24] },
  { date: "Mon Aug 11, 2025", numbers: [1,2,3,5,11,12,15,17,18,19,22,23] },
  { date: "Sat Aug 09, 2025", numbers: [4,5,10,11,12,13,16,18,19,21,23,24] },
  { date: "Fri Aug 08, 2025", numbers: [1,2,5,6,9,11,12,15,18,19,22,24] },
  { date: "Thu Aug 07, 2025", numbers: [1,2,5,6,7,8,9,15,16,18,19,23] },
  { date: "Wed Aug 06, 2025", numbers: [4,6,8,10,11,12,15,16,17,19,21,24] },
  { date: "Tue Aug 05, 2025", numbers: [1,2,5,8,10,11,14,16,17,18,19,22] },
  { date: "Mon Aug 04, 2025", numbers: [1,2,5,9,11,12,14,15,16,17,22,23] },
  { date: "Sat Aug 02, 2025", numbers: [2,4,5,6,8,9,10,11,12,16,19,24] },
  { date: "Fri Aug 01, 2025", numbers: [2,4,5,7,8,9,12,16,17,19,21,22] },
];

const N = lotteryData.length;
const drawMasks = lotteryData.map(d => d.numbers.reduce((m, n) => m | (1 << (n - 1)), 0));

const allFreq = new Array(25).fill(0);
lotteryData.forEach(d => d.numbers.forEach(n => allFreq[n]++));
const freqMin = Math.min(...allFreq.slice(1));
const freqMax = Math.max(...allFreq.slice(1));

function popcount(x) {
  x = x - ((x >> 1) & 0x55555555);
  x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
  x = (x + (x >> 4)) & 0x0f0f0f0f;
  return (x * 0x01010101) >>> 24;
}
function toBitmask(nums) { return nums.reduce((m, n) => m | (1 << (n - 1)), 0); }
function maskToNums(mask) { const r = []; for (let i = 0; i < 24; i++) if (mask & (1 << i)) r.push(i + 1); return r; }
function gosper(v) { const u = v & -v; const w = u + v; return w | (((w ^ v) / u) >> 2); }
function heatColor(n) {
  const t = (allFreq[n] - freqMin) / (freqMax - freqMin) || 0;
  const h = Math.round(220 - t * 220);
  return `hsl(${h},${Math.round(55 + t * 20)}%,${Math.round(88 - t * 32)}%)`;
}

function score(mask) {
  let net = -(N * 2), wins = 0, big = 0, prev = -1, totalGap = 0, gapCount = 0;
  for (let i = 0; i < N; i++) {
    const m = popcount(drawMasks[i] & mask);
    net += PRIZES[m];
    if (m === 1 || m === 11) big++;
    if (m <= 3 || m >= 9) {
      wins++;
      if (prev >= 0) { totalGap += i - prev; gapCount++; }
      prev = i;
    }
  }
  return { net, wins, big, avgGap: gapCount > 0 ? totalGap / gapCount : Infinity };
}

function analyzeSelection(selected) {
  if (selected.size !== 12) return null;
  const mask = toBitmask([...selected]);
  const results = lotteryData.map((d, idx) => {
    const m = popcount(drawMasks[idx] & mask);
    return { date: d.date, matches: m, prize: PRIZES[m], isWin: m <= 3 || m >= 9, idx };
  });
  const wins = results.filter(r => r.isWin).length;
  const totalCost = N * 2;
  const totalWinnings = results.reduce((s, r) => s + r.prize, 0);
  const netProfit = totalWinnings - totalCost;
  const roi = ((netProfit / totalCost) * 100).toFixed(1);
  const winIndices = results.reduce((a, r, i) => { if (r.isWin) a.push(i); return a; }, []);
  let avgDrawsBetweenWins;
  if (winIndices.length > 1) {
    let g = 0; for (let i = 1; i < winIndices.length; i++) g += winIndices[i] - winIndices[i - 1];
    avgDrawsBetweenWins = (g / (winIndices.length - 1)).toFixed(1);
  } else { avgDrawsBetweenWins = winIndices.length === 1 ? 'Only 1 win' : 'No wins'; }
  const matchDist = {};
  for (let i = 0; i <= 12; i++) matchDist[i] = results.filter(r => r.matches === i).length;
  let longestWin = 0, longestLoss = 0, cw = 0, cl = 0;
  results.forEach(r => {
    if (r.isWin) { cw++; cl = 0; if (cw > longestWin) longestWin = cw; }
    else { cl++; cw = 0; if (cl > longestLoss) longestLoss = cl; }
  });
  let currentStreak = 0;
  const isCurrentWin = results[0]?.isWin;
  for (const r of results) { if (r.isWin === isCurrentWin) currentStreak++; else break; }
  const selArr = [...selected];
  const oddCount = selArr.filter(n => n % 2 === 1).length;
  const lowCount = selArr.filter(n => n <= 8).length;
  const midCount = selArr.filter(n => n >= 9 && n <= 16).length;
  return {
    results, wins, losses: N - wins,
    winRate: (wins / N * 100).toFixed(1),
    matchDist, totalCost, totalWinnings, netProfit, roi,
    avgDrawsBetweenWins, longestWin, longestLoss, currentStreak, isCurrentWin,
    oddCount, evenCount: 12 - oddCount, lowCount, midCount, highCount: 12 - lowCount - midCount,
  };
}

function predictNext() {
  const f = new Array(25).fill(0);
  lotteryData.slice(0, 30).forEach(d => d.numbers.forEach(n => f[n]++));
  const ranked = Array.from({ length: 24 }, (_, i) => i + 1).sort((a, b) => f[b] - f[a]);
  return [...ranked.slice(0, 6), ...ranked.slice(18)].sort((a, b) => a - b);
}
function suggestNums() {
  const ranked = Array.from({ length: 24 }, (_, i) => i + 1).sort((a, b) => allFreq[b] - allFreq[a]);
  return [...ranked.slice(0, 4), ...ranked.slice(10, 14), ...ranked.slice(20)].sort((a, b) => a - b);
}
function randomPick() {
  const arr = Array.from({ length: 24 }, (_, i) => i + 1);
  for (let i = 23; i >= 12; i--) { const j = Math.floor(Math.random() * (i + 1)); [arr[i], arr[j]] = [arr[j], arr[i]]; }
  return arr.slice(12).sort((a, b) => a - b);
}

function SortIcon({ col, sortConfig }) {
  if (sortConfig.key !== col) return <ArrowUpDown size={12} className="inline ml-1 opacity-40" />;
  return sortConfig.dir === 'asc'
    ? <ArrowUp size={12} className="inline ml-1" />
    : <ArrowDown size={12} className="inline ml-1" />;
}

const FIRST_MASK = 0xFFF;
const LAST_MASK = 0xFFF000;
const TOTAL_COMBOS = 2704156;
const CHUNK = 20000;

export default function App() {
  const [selectedNumbers, setSelectedNumbers] = useState(new Set());
  const [showDetails, setShowDetails] = useState(false);
  const [searching, setSearching] = useState(false);
  const [searchProgress, setSearchProgress] = useState(0);
  const [bestFound, setBestFound] = useState(null);
  const [suggested, setSuggested] = useState(null);
  const [trendPick, setTrendPick] = useState(null);
  const [filter50Plus, setFilter50Plus] = useState(false);
  const [sortConfig, setSortConfig] = useState({ key: null, dir: 'desc' });
  const [savedPicks, setSavedPicks] = useState([]);
  const [showComparison, setShowComparison] = useState(false);
  const [showFreqChart, setShowFreqChart] = useState(false);
  const searchGen = useRef(0);

  const analysis = useMemo(() => analyzeSelection(selectedNumbers), [selectedNumbers]);

  const sortedRows = useMemo(() => {
    if (!analysis) return [];
    const rows = filter50Plus ? analysis.results.filter(r => r.prize >= 50) : [...analysis.results];
    if (!sortConfig.key) return rows;
    return [...rows].sort((a, b) => {
      const dir = sortConfig.dir === 'asc' ? 1 : -1;
      if (sortConfig.key === 'matches') return (a.matches - b.matches) * dir;
      if (sortConfig.key === 'prize') return (a.prize - b.prize) * dir;
      if (sortConfig.key === 'date') return (a.idx - b.idx) * (sortConfig.dir === 'asc' ? -1 : 1);
      return 0;
    });
  }, [analysis, filter50Plus, sortConfig]);

  const toggleNumber = (num) => {
    const s = new Set(selectedNumbers);
    if (s.has(num)) s.delete(num);
    else if (s.size < 12) s.add(num);
    setSelectedNumbers(s);
  };

  const handleSort = (key) => {
    setSortConfig(prev => prev.key === key
      ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' }
      : { key, dir: 'desc' });
  };

  const handleFindBest = () => {
    searchGen.current++;
    const myGen = searchGen.current;
    setSearching(true); setSearchProgress(0);
    setTrendPick(null); setSuggested(null); setBestFound(null);
    let best = { net: -Infinity, wins: 0, big: 0, avgGap: Infinity, mask: FIRST_MASK };
    let mask = FIRST_MASK, done = 0;
    const tick = () => {
      if (searchGen.current !== myGen) return;
      let c = 0;
      while (c < CHUNK && mask <= LAST_MASK) {
        const s = score(mask);
        if (s.net > best.net || (s.net === best.net && s.wins > best.wins)) best = { ...s, mask };
        mask = gosper(mask); c++; done++;
      }
      setSearchProgress(Math.round((done / TOTAL_COMBOS) * 100));
      if (mask <= LAST_MASK) { setTimeout(tick, 0); }
      else {
        if (searchGen.current !== myGen) return;
        const nums = maskToNums(best.mask);
        setSearching(false);
        setSelectedNumbers(new Set(nums));
        setBestFound({ numbers: nums, wins: best.wins, profit: best.net, count1or11: best.big, avgGap: isFinite(best.avgGap) ? best.avgGap.toFixed(1) : 'N/A' });
      }
    };
    setTimeout(tick, 0);
  };

  const handlePredictNext = () => {
    const nums = predictNext();
    setSelectedNumbers(new Set(nums));
    setTrendPick({ numbers: nums, strategy: "6 numbers with recent momentum + 6 numbers due (haven't appeared recently)", window: "Last 30 draws" });
    setSuggested(null); setBestFound(null);
  };

  const handleSuggest = () => {
    const nums = suggestNums();
    setSelectedNumbers(new Set(nums));
    setSuggested({ numbers: nums, strategy: "Balanced mix of hot (top 4), warm (middle 4), and cold (bottom 4) numbers" });
    setTrendPick(null); setBestFound(null);
  };

  const handleRandomPick = () => {
    setSelectedNumbers(new Set(randomPick()));
    setTrendPick(null); setSuggested(null); setBestFound(null);
  };

  const handleSavePick = () => {
    if (!analysis || savedPicks.length >= 3) return;
    const nums = [...selectedNumbers].sort((a, b) => a - b);
    if (savedPicks.some(p => p.numbers.join() === nums.join())) return;
    setSavedPicks(prev => [...prev, { numbers: nums, analysis: { ...analysis, results: undefined } }]);
  };

  const clearAll = () => {
    setSelectedNumbers(new Set());
    setBestFound(null); setSuggested(null); setTrendPick(null);
  };

  const freqChartMax = Math.max(...allFreq.slice(1));

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg">
      <div className="bg-white rounded-lg p-6 mb-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold text-indigo-900">Texas All or Nothing Analyzer</h1>
          <button
            onClick={() => setShowFreqChart(v => !v)}
            className={`flex items-center gap-1 text-sm px-3 py-2 rounded-lg transition-colors ${showFreqChart ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
          >
            <BarChart2 size={16} /> Freq Chart
          </button>
        </div>
        <p className="text-gray-600 mb-4">📊 {N} draws (August 1, 2025 – May 6, 2026)</p>

        {/* Collapsible frequency bar chart */}
        {showFreqChart && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Number Draw Frequency (all {N} draws)</h3>
            <div className="space-y-1">
              {Array.from({ length: 24 }, (_, i) => i + 1).map(n => (
                <div key={n} className="flex items-center gap-2">
                  <span className="w-6 text-xs text-right font-mono text-gray-600">{n}</span>
                  <div className="flex-1 bg-gray-200 rounded h-4 overflow-hidden">
                    <div className="h-full rounded" style={{ width: `${(allFreq[n] / freqChartMax) * 100}%`, backgroundColor: heatColor(n) }} />
                  </div>
                  <span className="w-7 text-xs text-gray-500 font-mono">{allFreq[n]}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
          <h3 className="font-bold text-blue-900 mb-1">🎯 Win Strategy</h3>
          <p className="text-sm text-blue-800">
            <strong>WIN:</strong> 0–3 or 9–12 matches &nbsp;|&nbsp;
            <strong>BREAK EVEN:</strong> 4 or 8 ($2) &nbsp;|&nbsp;
            <strong>LOSE:</strong> 5, 6, 7 ($0)
          </p>
        </div>

        {/* Controls */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
            <h2 className="text-lg font-semibold text-gray-700">Select 12 Numbers</h2>
            <div className="flex flex-wrap gap-2">
              <button onClick={handlePredictNext} className="text-sm font-medium px-4 py-2 rounded bg-orange-600 hover:bg-orange-700 text-white transition-colors">
                🎯 Predict Next
              </button>
              <button onClick={handleSuggest} className="text-sm font-medium px-4 py-2 rounded bg-purple-600 hover:bg-purple-700 text-white transition-colors">
                💡 Suggest
              </button>
              <button
                onClick={handleFindBest}
                disabled={searching}
                className={`text-sm font-medium px-4 py-2 rounded transition-colors ${searching ? 'bg-gray-400 cursor-not-allowed text-white' : 'bg-green-600 hover:bg-green-700 text-white'}`}
              >
                {searching ? `Searching ${Math.round(searchProgress)}%…` : '🔍 Find Best (2.7M)'}
              </button>
              <button onClick={handleRandomPick} className="flex items-center gap-1 text-sm font-medium px-4 py-2 rounded bg-teal-600 hover:bg-teal-700 text-white transition-colors">
                <Shuffle size={14} /> Random
              </button>
              {analysis && savedPicks.length < 3 && (
                <button onClick={handleSavePick} className="flex items-center gap-1 text-sm font-medium px-3 py-2 rounded bg-yellow-500 hover:bg-yellow-600 text-white transition-colors">
                  <Bookmark size={14} /> Save
                </button>
              )}
              {selectedNumbers.size > 0 && (
                <button onClick={clearAll} className="text-sm text-red-600 hover:text-red-800 font-medium px-3 py-2 transition-colors">
                  Clear All
                </button>
              )}
            </div>
          </div>

          {/* Progress bar */}
          {searching && (
            <div className="mb-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full transition-all" style={{ width: `${searchProgress}%` }} />
              </div>
              <p className="text-xs text-gray-600 mt-1 text-center">Testing all 2,704,156 combinations…</p>
            </div>
          )}

          {/* Strategy info boxes */}
          {trendPick && (
            <div className="mb-4 p-4 bg-orange-50 border-2 border-orange-300 rounded-lg">
              <h3 className="font-bold text-orange-800 mb-1">🎯 Trend-Based Prediction</h3>
              <p className="text-sm text-orange-700 mb-1">
                <strong>Numbers:</strong> {trendPick.numbers.join(', ')}<br />
                <strong>Strategy:</strong> {trendPick.strategy}<br />
                <strong>Analysis:</strong> {trendPick.window}
              </p>
              <p className="text-xs text-orange-600 italic">Lottery draws are random. Past patterns don't predict future results.</p>
            </div>
          )}
          {suggested && (
            <div className="mb-4 p-4 bg-purple-50 border-2 border-purple-300 rounded-lg">
              <h3 className="font-bold text-purple-800 mb-1">💡 Suggested Combination</h3>
              <p className="text-sm text-purple-700 mb-1">
                <strong>Numbers:</strong> {suggested.numbers.join(', ')}<br />
                <strong>Strategy:</strong> {suggested.strategy}
              </p>
              <p className="text-xs text-purple-600 italic">Strategic selection based on historical frequency, not a prediction.</p>
            </div>
          )}
          {bestFound && (
            <div className="mb-4 p-4 bg-green-50 border-2 border-green-300 rounded-lg">
              <h3 className="font-bold text-green-800 mb-1">🏆 Best Combination Found!</h3>
              <p className="text-sm text-green-700">
                <strong>Numbers:</strong> {bestFound.numbers.join(', ')}<br />
                <strong>Total Wins:</strong> {bestFound.wins} / {N} draws &nbsp;|&nbsp;
                <strong>1 or 11 matches:</strong> {bestFound.count1or11}× ($500)<br />
                <strong>Net Profit:</strong> ${bestFound.profit.toLocaleString()} &nbsp;|&nbsp;
                <strong>Avg gap:</strong> {bestFound.avgGap !== 'N/A' ? `${bestFound.avgGap} draws` : 'N/A'}
              </p>
            </div>
          )}

          {/* Number grid with heatmap */}
          <div className="grid grid-cols-8 gap-2">
            {Array.from({ length: 24 }, (_, i) => i + 1).map(num => {
              const isSel = selectedNumbers.has(num);
              return (
                <button
                  key={num}
                  onClick={() => toggleNumber(num)}
                  disabled={selectedNumbers.size >= 12 && !isSel}
                  title={`Number ${num}: drawn ${allFreq[num]}×`}
                  className={`h-12 rounded-lg font-bold text-lg transition-all border-2 ${
                    isSel
                      ? 'bg-indigo-600 text-white shadow-md scale-105 border-indigo-700'
                      : 'text-gray-800 hover:scale-105 border-transparent'
                  } ${selectedNumbers.size >= 12 && !isSel ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}`}
                  style={!isSel ? { backgroundColor: heatColor(num) } : undefined}
                >
                  {num}
                </button>
              );
            })}
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-3 rounded" style={{ backgroundColor: 'hsl(220,55%,88%)' }} /> Cold
            </span>
            <span>Selected: {selectedNumbers.size}/12 {selectedNumbers.size === 12 && '✓'}</span>
            <span className="flex items-center gap-1">
              Hot <span className="inline-block w-3 h-3 rounded" style={{ backgroundColor: 'hsl(0,75%,56%)' }} />
            </span>
          </div>
        </div>

        {/* Saved picks */}
        {savedPicks.length > 0 && (
          <div className="mt-2">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-700">Saved Picks ({savedPicks.length}/3)</h3>
              <button onClick={() => setShowComparison(v => !v)} className="text-sm text-indigo-600 hover:text-indigo-800 font-medium">
                {showComparison ? 'Hide Comparison' : 'Compare'}
              </button>
            </div>
            {showComparison ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {savedPicks.map((pick, i) => (
                  <div key={i} className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-yellow-800 text-sm">Pick #{i + 1}</span>
                      <button onClick={() => setSavedPicks(prev => prev.filter((_, j) => j !== i))} className="text-red-400 hover:text-red-600 text-xs">✕</button>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">{pick.numbers.join(', ')}</p>
                    <div className="space-y-1 text-xs">
                      {[['Wins', pick.analysis.wins, 'text-green-700'],
                        ['Win Rate', `${pick.analysis.winRate}%`, ''],
                        ['Net', `${pick.analysis.netProfit >= 0 ? '+' : ''}$${pick.analysis.netProfit}`, pick.analysis.netProfit >= 0 ? 'text-green-600' : 'text-red-600'],
                        ['ROI', `${pick.analysis.roi}%`, parseFloat(pick.analysis.roi) >= 0 ? 'text-green-600' : 'text-red-600']
                      ].map(([label, val, cls]) => (
                        <div key={label} className="flex justify-between">
                          <span className="text-gray-500">{label}</span>
                          <span className={`font-semibold ${cls}`}>{val}</span>
                        </div>
                      ))}
                    </div>
                    <button
                      onClick={() => { setSelectedNumbers(new Set(pick.numbers)); setBestFound(null); setSuggested(null); setTrendPick(null); }}
                      className="mt-2 w-full text-xs bg-yellow-200 hover:bg-yellow-300 text-yellow-800 font-medium py-1 rounded transition-colors"
                    >
                      Load
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex gap-2 flex-wrap">
                {savedPicks.map((pick, i) => (
                  <div key={i} className="flex items-center gap-1 bg-yellow-100 border border-yellow-300 rounded px-2 py-1">
                    <span className="text-xs text-yellow-800 font-medium">#{i + 1}: {pick.numbers.slice(0, 4).join(',')}…</span>
                    <button onClick={() => { setSelectedNumbers(new Set(pick.numbers)); setBestFound(null); setSuggested(null); setTrendPick(null); }} className="text-xs text-indigo-600 hover:text-indigo-800">Load</button>
                    <button onClick={() => setSavedPicks(prev => prev.filter((_, j) => j !== i))} className="text-xs text-red-400 hover:text-red-600">✕</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Analysis results */}
      {analysis && (
        <div className="bg-white rounded-lg p-6">
          <h2 className="text-2xl font-bold text-indigo-900 mb-4">Analysis Results</h2>

          {/* Balance stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Odd / Even Balance</h3>
              <div className="flex h-4 rounded overflow-hidden mb-1">
                <div className="bg-blue-400" style={{ width: `${(analysis.oddCount / 12) * 100}%` }} />
                <div className="bg-blue-200 flex-1" />
              </div>
              <div className="flex justify-between text-xs text-gray-600">
                <span className="text-blue-700 font-medium">{analysis.oddCount} odd</span>
                <span className="text-blue-500">{analysis.evenCount} even</span>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Low (1–8) / Mid (9–16) / High (17–24)</h3>
              <div className="flex gap-0.5 h-4 mb-1">
                <div className="bg-green-400 rounded-l" style={{ flex: analysis.lowCount || 0.1 }} />
                <div className="bg-yellow-400" style={{ flex: analysis.midCount || 0.1 }} />
                <div className="bg-red-400 rounded-r" style={{ flex: analysis.highCount || 0.1 }} />
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-green-700 font-medium">{analysis.lowCount} low</span>
                <span className="text-yellow-700 font-medium">{analysis.midCount} mid</span>
                <span className="text-red-700 font-medium">{analysis.highCount} high</span>
              </div>
            </div>
          </div>

          {/* Financial summary */}
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-5 mb-6 border-2 border-purple-200">
            <h3 className="text-xl font-bold text-purple-900 mb-3">💰 Financial Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div><p className="text-sm text-gray-600">Spent</p><p className="text-2xl font-bold text-red-600">-${analysis.totalCost}</p></div>
              <div><p className="text-sm text-gray-600">Won</p><p className="text-2xl font-bold text-green-600">+${analysis.totalWinnings}</p></div>
              <div>
                <p className="text-sm text-gray-600">Net</p>
                <p className={`text-2xl font-bold ${analysis.netProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {analysis.netProfit >= 0 ? '+' : ''}${analysis.netProfit}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">ROI</p>
                <p className={`text-2xl font-bold ${parseFloat(analysis.roi) >= 0 ? 'text-green-600' : 'text-red-600'}`}>{analysis.roi}%</p>
              </div>
            </div>
          </div>

          {/* Win/Loss/Rate + Streaks */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
                <div className="flex items-center justify-center mb-1"><CheckCircle className="text-green-600 mr-1" size={20} /><span className="text-2xl font-bold text-green-700">{analysis.wins}</span></div>
                <p className="text-center text-xs text-green-800 font-medium">Wins</p>
              </div>
              <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
                <div className="flex items-center justify-center mb-1"><XCircle className="text-red-600 mr-1" size={20} /><span className="text-2xl font-bold text-red-700">{analysis.losses}</span></div>
                <p className="text-center text-xs text-red-800 font-medium">Losses</p>
              </div>
              <div className="bg-indigo-50 rounded-lg p-4 border-2 border-indigo-200">
                <div className="flex items-center justify-center mb-1"><AlertCircle className="text-indigo-600 mr-1" size={20} /><span className="text-2xl font-bold text-indigo-700">{analysis.winRate}%</span></div>
                <p className="text-center text-xs text-indigo-800 font-medium">Rate</p>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Streak Stats</h3>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="text-lg font-bold text-green-600">{analysis.longestWin}</p>
                  <p className="text-xs text-gray-500">Longest Win</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-red-600">{analysis.longestLoss}</p>
                  <p className="text-xs text-gray-500">Longest Loss</p>
                </div>
                <div>
                  <p className={`text-lg font-bold ${analysis.isCurrentWin ? 'text-green-600' : 'text-red-600'}`}>{analysis.currentStreak}</p>
                  <p className="text-xs text-gray-500">Current {analysis.isCurrentWin ? 'Win' : 'Loss'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Win Frequency */}
          <div className="bg-blue-50 rounded-lg p-4 border-2 border-blue-200 mb-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2 text-center">Win Frequency</h3>
            <p className="text-center text-3xl font-bold text-blue-700">
              {/^\d/.test(String(analysis.avgDrawsBetweenWins))
                ? `Every ${analysis.avgDrawsBetweenWins} draws`
                : analysis.avgDrawsBetweenWins}
            </p>
            <p className="text-center text-sm text-blue-600 mt-1">Average gap between wins</p>
          </div>

          {/* Match Distribution */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">Match Distribution</h3>
            <div className="space-y-2">
              {Object.entries(analysis.matchDist).map(([matches, count]) => {
                const m = parseInt(matches);
                const isWin = m <= 3 || m >= 9;
                const pct = (count / N * 100).toFixed(1);
                const prizeText = m === 0 || m === 12 ? '$250K' : m === 1 || m === 11 ? '$500' : m === 2 || m === 10 ? '$50' : m === 3 || m === 9 ? '$10' : m === 4 || m === 8 ? '$2' : '$0';
                return (
                  <div key={matches} className="flex items-center gap-2">
                    <span className={`w-28 text-sm font-medium ${isWin ? 'text-green-700' : 'text-gray-600'}`}>{matches} ({prizeText}):</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                      <div className={`h-full rounded-full ${isWin ? 'bg-green-500' : 'bg-gray-400'}`} style={{ width: `${Math.max(parseFloat(pct), 2)}%` }} />
                      <span className="absolute inset-0 flex items-center justify-center text-xs font-semibold text-gray-800">{count} ({pct}%)</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sortable detailed results table */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <button onClick={() => setShowDetails(!showDetails)} className="bg-indigo-100 hover:bg-indigo-200 text-indigo-800 font-semibold py-2 px-4 rounded-lg transition-colors">
                {showDetails ? 'Hide' : 'Show'} Detailed Results
              </button>
              {showDetails && (
                <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input type="checkbox" checked={filter50Plus} onChange={e => setFilter50Plus(e.target.checked)} className="rounded" />
                  Show only $50+ wins
                </label>
              )}
            </div>
            {showDetails && (
              <div className="max-h-96 overflow-y-auto border rounded-lg">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100 sticky top-0">
                    <tr>
                      <th className="px-4 py-2 text-left cursor-pointer hover:bg-gray-200 select-none" onClick={() => handleSort('date')}>
                        Date <SortIcon col="date" sortConfig={sortConfig} />
                      </th>
                      <th className="px-4 py-2 text-center cursor-pointer hover:bg-gray-200 select-none" onClick={() => handleSort('matches')}>
                        Matches <SortIcon col="matches" sortConfig={sortConfig} />
                      </th>
                      <th className="px-4 py-2 text-center cursor-pointer hover:bg-gray-200 select-none" onClick={() => handleSort('prize')}>
                        Prize <SortIcon col="prize" sortConfig={sortConfig} />
                      </th>
                      <th className="px-4 py-2 text-center">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedRows.map((result, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-4 py-2 text-gray-700">{result.date}</td>
                        <td className="px-4 py-2 text-center font-semibold">{result.matches}</td>
                        <td className="px-4 py-2 text-center font-bold text-green-600">${result.prize}</td>
                        <td className="px-4 py-2 text-center">
                          {result.isWin
                            ? <span className="text-green-700 font-medium">✓ Win</span>
                            : <span className="text-gray-600">Loss</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {!analysis && selectedNumbers.size > 0 && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <p className="text-yellow-800">
            Select {12 - selectedNumbers.size} more number{12 - selectedNumbers.size !== 1 ? 's' : ''} to analyze.
          </p>
        </div>
      )}
    </div>
  );
}
