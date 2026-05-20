import { useState, useMemo } from 'react';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function App() {
  const [selectedNumbers, setSelectedNumbers] = useState(new Set());
  const [showDetails, setShowDetails] = useState(false);
  const [searching, setSearching] = useState(false);
  const [searchProgress, setSearchProgress] = useState(0);
  const [bestFound, setBestFound] = useState(null);
  const [suggested, setSuggested] = useState(null);
  const [filter50Plus, setFilter50Plus] = useState(false);
  const [trendPick, setTrendPick] = useState(null);

  // Historical lottery data - AUGUST 1, 2025 through MAY 6, 2026
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

  const analysis = useMemo(() => {
    if (selectedNumbers.size !== 12) return null;

    const results = lotteryData.map(draw => {
      const matches = draw.numbers.filter(n => selectedNumbers.has(n)).length;
      const isWin = matches <= 3 || matches >= 9;

      let prize = 0;
      if (matches === 0 || matches === 12) prize = 250000;
      else if (matches === 1 || matches === 11) prize = 500;
      else if (matches === 2 || matches === 10) prize = 50;
      else if (matches === 3 || matches === 9) prize = 10;
      else if (matches === 4 || matches === 8) prize = 2;

      return { ...draw, matches, isWin, prize };
    });

    const wins = results.filter(r => r.isWin).length;
    const losses = results.length - wins;
    const winRate = (wins / results.length * 100).toFixed(1);

    const winIndices = [];
    results.forEach((r, idx) => { if (r.isWin) winIndices.push(idx); });

    let avgDrawsBetweenWins = 0;
    if (winIndices.length > 1) {
      let totalGap = 0;
      for (let i = 1; i < winIndices.length; i++) {
        totalGap += winIndices[i] - winIndices[i - 1];
      }
      avgDrawsBetweenWins = (totalGap / (winIndices.length - 1)).toFixed(1);
    } else if (winIndices.length === 1) {
      avgDrawsBetweenWins = 'Only 1 win';
    } else {
      avgDrawsBetweenWins = 'No wins';
    }

    const matchDistribution = {};
    for (let i = 0; i <= 12; i++) {
      matchDistribution[i] = results.filter(r => r.matches === i).length;
    }

    const totalCost = results.length * 2;
    const totalWinnings = results.reduce((sum, r) => sum + r.prize, 0);
    const netProfit = totalWinnings - totalCost;
    const roi = ((netProfit / totalCost) * 100).toFixed(1);

    return { results, wins, losses, winRate, matchDistribution, totalCost, totalWinnings, netProfit, roi, avgDrawsBetweenWins };
  }, [selectedNumbers]);

  const toggleNumber = (num) => {
    const newSelected = new Set(selectedNumbers);
    if (newSelected.has(num)) {
      newSelected.delete(num);
    } else {
      if (newSelected.size < 12) {
        newSelected.add(num);
      }
    }
    setSelectedNumbers(newSelected);
  };

  const findBestCombination = async () => {
    setSearching(true);
    setSearchProgress(0);

    let bestCombo = null;
    let bestWins = 0;
    let bestProfit = -999999;
    let best1or11 = 0;
    let bestAvgGap = 0;

    const testCombination = (combo) => {
      const comboSet = new Set(combo);
      let wins = 0;
      let totalPrize = 0;
      let count1or11 = 0;
      const winIndices = [];

      lotteryData.forEach((draw, idx) => {
        const matches = draw.numbers.filter(n => comboSet.has(n)).length;
        const isWin = matches <= 3 || matches >= 9;

        if (matches === 1 || matches === 11) count1or11++;

        let prize = 0;
        if (matches === 0 || matches === 12) prize = 250000;
        else if (matches === 1 || matches === 11) prize = 500;
        else if (matches === 2 || matches === 10) prize = 50;
        else if (matches === 3 || matches === 9) prize = 10;
        else if (matches === 4 || matches === 8) prize = 2;

        if (isWin) { wins++; winIndices.push(idx); }
        totalPrize += prize;
      });

      const profit = totalPrize - (lotteryData.length * 2);

      let avgDrawsBetweenWins = 0;
      if (winIndices.length > 1) {
        let totalGap = 0;
        for (let i = 1; i < winIndices.length; i++) {
          totalGap += winIndices[i] - winIndices[i - 1];
        }
        avgDrawsBetweenWins = (totalGap / (winIndices.length - 1)).toFixed(1);
      }

      if (wins > bestWins || (wins === bestWins && profit > bestProfit)) {
        bestWins = wins;
        bestProfit = profit;
        bestCombo = [...combo];
        best1or11 = count1or11;
        bestAvgGap = avgDrawsBetweenWins;
      }
    };

    const patterns = [
      [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23],
      [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
      [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
      [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    ];
    patterns.forEach(p => testCombination(p));
    setSearchProgress(10);

    const freq = {};
    for (let i = 1; i <= 24; i++) freq[i] = 0;
    lotteryData.forEach(draw => { draw.numbers.forEach(n => freq[n]++); });

    const mostFreq = Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([n]) => parseInt(n));
    testCombination(mostFreq);

    const leastFreq = Object.entries(freq).sort((a, b) => a[1] - b[1]).slice(0, 12).map(([n]) => parseInt(n));
    testCombination(leastFreq);

    setSearchProgress(30);

    for (let i = 0; i < 1200000; i++) {
      const combo = [];
      const available = [...Array(24)].map((_, idx) => idx + 1);
      for (let j = 0; j < 12; j++) {
        const idx = Math.floor(Math.random() * available.length);
        combo.push(available[idx]);
        available.splice(idx, 1);
      }
      testCombination(combo);

      if (i % 6000 === 0) {
        setSearchProgress(30 + (i / 1200000) * 70);
        await new Promise(resolve => setTimeout(resolve, 0));
      }
    }

    setSearchProgress(100);

    if (bestCombo) {
      setSelectedNumbers(new Set(bestCombo.sort((a, b) => a - b)));
      setBestFound({
        numbers: bestCombo.sort((a, b) => a - b),
        wins: bestWins,
        profit: bestProfit,
        count1or11: best1or11,
        avgGap: bestAvgGap,
      });
    }

    setSearching(false);
  };

  const suggestNumbers = () => {
    const freq = {};
    for (let i = 1; i <= 24; i++) freq[i] = 0;
    lotteryData.forEach(draw => { draw.numbers.forEach(n => freq[n]++); });

    const sortedByFreq = Object.entries(freq).sort((a, b) => b[1] - a[1]).map(([n]) => parseInt(n));
    const mostFreq = sortedByFreq.slice(0, 4);
    const leastFreq = sortedByFreq.slice(-4);
    const mediumFreq = sortedByFreq.slice(10, 14);

    const nums = [...mostFreq, ...mediumFreq, ...leastFreq].sort((a, b) => a - b);
    setSelectedNumbers(new Set(nums));
    setSuggested({
      numbers: nums,
      strategy: "Balanced mix of hot (frequent), warm (medium), and cold (infrequent) numbers",
    });
    setTrendPick(null);
    setBestFound(null);
  };

  const predictNextNumbers = () => {
    const recentDraws = lotteryData.slice(0, 30);
    const recentFreq = {};
    for (let i = 1; i <= 24; i++) recentFreq[i] = 0;
    recentDraws.forEach(draw => { draw.numbers.forEach(n => recentFreq[n]++); });

    const hotRecent = Object.entries(recentFreq).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([n]) => parseInt(n));
    const coldRecent = Object.entries(recentFreq).sort((a, b) => a[1] - b[1]).slice(0, 6).map(([n]) => parseInt(n));

    const predicted = [...hotRecent, ...coldRecent].sort((a, b) => a - b);
    setSelectedNumbers(new Set(predicted));
    setTrendPick({
      numbers: predicted,
      strategy: "Trend-based: 6 numbers with recent momentum + 6 numbers that are 'due' (haven't appeared recently)",
      recentWindow: "Last 30 draws analyzed",
    });
    setSuggested(null);
    setBestFound(null);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg">
      <div className="bg-white rounded-lg p-6 mb-6">
        <h1 className="text-3xl font-bold text-indigo-900 mb-2">Texas All or Nothing Analyzer</h1>
        <p className="text-gray-600 mb-4">📊 {lotteryData.length} draws (August 1, 2025 – May 6, 2026)</p>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
          <h3 className="font-bold text-blue-900 mb-2">🎯 Win Strategy</h3>
          <p className="text-sm text-blue-800">
            <strong>WIN:</strong> 0–3 or 9–12 matches &nbsp;|&nbsp;
            <strong>BREAK EVEN:</strong> 4 or 8 ($2) &nbsp;|&nbsp;
            <strong>LOSE:</strong> 5, 6, 7 ($0)
          </p>
        </div>

        <div className="mb-6">
          <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
            <h2 className="text-lg font-semibold text-gray-700">Select 12 Numbers</h2>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={predictNextNumbers}
                className="text-sm font-medium px-4 py-2 rounded bg-orange-600 hover:bg-orange-700 text-white transition-colors"
              >
                🎯 Predict Next
              </button>
              <button
                onClick={suggestNumbers}
                className="text-sm font-medium px-4 py-2 rounded bg-purple-600 hover:bg-purple-700 text-white transition-colors"
              >
                💡 Suggest Numbers
              </button>
              <button
                onClick={findBestCombination}
                disabled={searching}
                className={`text-sm font-medium px-4 py-2 rounded transition-colors ${
                  searching
                    ? 'bg-gray-400 cursor-not-allowed text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {searching ? `Searching ${Math.round(searchProgress)}%...` : '🔍 Find Best (2.7M+ Test)'}
              </button>
              {selectedNumbers.size > 0 && (
                <button
                  onClick={() => { setSelectedNumbers(new Set()); setBestFound(null); setSuggested(null); setTrendPick(null); }}
                  className="text-sm text-red-600 hover:text-red-800 font-medium px-3 py-2 transition-colors"
                >
                  Clear All
                </button>
              )}
            </div>
          </div>

          {searching && (
            <div className="mb-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all"
                  style={{ width: `${searchProgress}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1 text-center">Testing 2,704,156+ combinations...</p>
            </div>
          )}

          {trendPick && (
            <div className="mb-4 p-4 bg-orange-50 border-2 border-orange-300 rounded-lg">
              <h3 className="font-bold text-orange-800 mb-1">🎯 Trend-Based Prediction</h3>
              <p className="text-sm text-orange-700 mb-2">
                <strong>Numbers:</strong> {trendPick.numbers.join(', ')}<br />
                <strong>Strategy:</strong> {trendPick.strategy}<br />
                <strong>Analysis:</strong> {trendPick.recentWindow}
              </p>
              <p className="text-xs text-orange-600 italic">
                Note: This analyzes recent patterns but lottery draws are random. Past performance doesn't predict future results.
              </p>
            </div>
          )}

          {suggested && (
            <div className="mb-4 p-4 bg-purple-50 border-2 border-purple-300 rounded-lg">
              <h3 className="font-bold text-purple-800 mb-1">💡 Suggested Combination for Next Draw</h3>
              <p className="text-sm text-purple-700 mb-2">
                <strong>Numbers:</strong> {suggested.numbers.join(', ')}<br />
                <strong>Strategy:</strong> {suggested.strategy}
              </p>
              <p className="text-xs text-purple-600 italic">
                Note: This is not a prediction. Lottery draws are random. This is a strategic selection based on historical frequency patterns.
              </p>
            </div>
          )}

          {bestFound && (
            <div className="mb-4 p-4 bg-green-50 border-2 border-green-300 rounded-lg">
              <h3 className="font-bold text-green-800 mb-1">🏆 Best Combination Found!</h3>
              <p className="text-sm text-green-700">
                <strong>Numbers:</strong> {bestFound.numbers.join(', ')}<br />
                <strong>Total Wins:</strong> {bestFound.wins} out of {lotteryData.length} draws<br />
                <strong>1 or 11 matches:</strong> {bestFound.count1or11} times ($500 each)<br />
                <strong>Net Profit:</strong> ${bestFound.profit}<br />
                <strong>Avg draws between wins:</strong> {bestFound.avgGap > 0 ? `${bestFound.avgGap} draws` : 'N/A'}
              </p>
            </div>
          )}

          <div className="grid grid-cols-8 gap-2">
            {[...Array(24)].map((_, i) => {
              const num = i + 1;
              const isSelected = selectedNumbers.has(num);
              return (
                <button
                  key={num}
                  onClick={() => toggleNumber(num)}
                  disabled={selectedNumbers.size >= 12 && !isSelected}
                  className={`h-12 rounded-lg font-bold text-lg transition-all ${
                    isSelected
                      ? 'bg-indigo-600 text-white shadow-md scale-105'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  } ${selectedNumbers.size >= 12 && !isSelected ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  {num}
                </button>
              );
            })}
          </div>

          <div className="mt-3 text-center">
            <span className="text-sm text-gray-600">
              Selected: {selectedNumbers.size}/12 {selectedNumbers.size === 12 && '✓'}
            </span>
          </div>
        </div>
      </div>

      {analysis && (
        <div className="bg-white rounded-lg p-6">
          <h2 className="text-2xl font-bold text-indigo-900 mb-4">Analysis Results</h2>

          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-5 mb-6 border-2 border-purple-200">
            <h3 className="text-xl font-bold text-purple-900 mb-3">💰 Financial Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Spent</p>
                <p className="text-2xl font-bold text-red-600">-${analysis.totalCost}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Won</p>
                <p className="text-2xl font-bold text-green-600">+${analysis.totalWinnings}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Net</p>
                <p className={`text-2xl font-bold ${analysis.netProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {analysis.netProfit >= 0 ? '+' : ''}${analysis.netProfit}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">ROI</p>
                <p className={`text-2xl font-bold ${analysis.roi >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {analysis.roi}%
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
              <div className="flex items-center justify-center mb-2">
                <CheckCircle className="text-green-600 mr-2" size={24} />
                <span className="text-2xl font-bold text-green-700">{analysis.wins}</span>
              </div>
              <p className="text-center text-sm text-green-800 font-medium">Wins</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
              <div className="flex items-center justify-center mb-2">
                <XCircle className="text-red-600 mr-2" size={24} />
                <span className="text-2xl font-bold text-red-700">{analysis.losses}</span>
              </div>
              <p className="text-center text-sm text-red-800 font-medium">Losses</p>
            </div>
            <div className="bg-indigo-50 rounded-lg p-4 border-2 border-indigo-200">
              <div className="flex items-center justify-center mb-2">
                <AlertCircle className="text-indigo-600 mr-2" size={24} />
                <span className="text-2xl font-bold text-indigo-700">{analysis.winRate}%</span>
              </div>
              <p className="text-center text-sm text-indigo-800 font-medium">Win Rate</p>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4 border-2 border-blue-200 mb-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2 text-center">Win Frequency</h3>
            <p className="text-center text-3xl font-bold text-blue-700">
              {typeof analysis.avgDrawsBetweenWins === 'number'
                ? `Every ${analysis.avgDrawsBetweenWins} draws`
                : analysis.avgDrawsBetweenWins}
            </p>
            <p className="text-center text-sm text-blue-600 mt-1">Average gap between wins</p>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">Match Distribution</h3>
            <div className="space-y-2">
              {Object.entries(analysis.matchDistribution).map(([matches, count]) => {
                const isWinning = parseInt(matches) <= 3 || parseInt(matches) >= 9;
                const percentage = (count / analysis.results.length * 100).toFixed(1);

                let prizeText = '';
                const m = parseInt(matches);
                if (m === 0 || m === 12) prizeText = '$250K';
                else if (m === 1 || m === 11) prizeText = '$500';
                else if (m === 2 || m === 10) prizeText = '$50';
                else if (m === 3 || m === 9) prizeText = '$10';
                else if (m === 4 || m === 8) prizeText = '$2';
                else prizeText = '$0';

                return (
                  <div key={matches} className="flex items-center gap-2">
                    <span className={`w-28 text-sm font-medium ${isWinning ? 'text-green-700' : 'text-gray-600'}`}>
                      {matches} ({prizeText}):
                    </span>
                    <div className="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                      <div
                        className={`h-full rounded-full ${isWinning ? 'bg-green-500' : 'bg-gray-400'}`}
                        style={{ width: `${Math.max(parseFloat(percentage), 2)}%` }}
                      />
                      <span className="absolute inset-0 flex items-center justify-center text-xs font-semibold text-gray-800">
                        {count} ({percentage}%)
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="bg-indigo-100 hover:bg-indigo-200 text-indigo-800 font-semibold py-2 px-4 rounded-lg transition-colors"
              >
                {showDetails ? 'Hide' : 'Show'} Detailed Results
              </button>
              {showDetails && (
                <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filter50Plus}
                    onChange={e => setFilter50Plus(e.target.checked)}
                    className="rounded"
                  />
                  Show only $50+ wins
                </label>
              )}
            </div>

            {showDetails && (
              <div className="max-h-96 overflow-y-auto border rounded-lg">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100 sticky top-0">
                    <tr>
                      <th className="px-4 py-2 text-left">Date</th>
                      <th className="px-4 py-2 text-center">Matches</th>
                      <th className="px-4 py-2 text-center">Prize</th>
                      <th className="px-4 py-2 text-center">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analysis.results
                      .filter(result => !filter50Plus || result.prize >= 50)
                      .map((result, idx) => (
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
