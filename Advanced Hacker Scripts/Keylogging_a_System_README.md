# Keylogging a System (Windows API Demo)

⚠️ **שימוש ב-Keylogging מותר אך ורק בסביבות מעבדה/מחקר ועל מערכות שבהן יש לך הרשאה מפורשת.**  
המדריך הזה מתאר את המבנה הלימודי-טכני של הסקריפט בלבד.

---

# 📌 קישורי MSDN / Microsoft Learn ל-APIs שרלוונטיים לקוד

- **GetForegroundWindow**  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getforegroundwindow](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getforegroundwindow)
    
- **GetWindowTextLengthA**  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowtextlengtha](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowtextlengtha)
    
- **GetWindowTextA**  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowtexta](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowtexta)
    
- **GetKeyState**  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getkeystate](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getkeystate)
    
- **GetKeyboardState**  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getkeyboardstate](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getkeyboardstate)
    
- **ToAscii** _(מיושן; ראו הערה למטה)_  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-toascii](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-toascii)
    
- **SetWindowsHookExA** (כולל ‎`WH_KEYBOARD_LL`)  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowshookexa](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowshookexa)
    
- **CallNextHookEx**  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-callnexthookex](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-callnexthookex)
    
- **GetMessageA**  
    [https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getmessagea](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getmessagea)
    
- **LowLevelKeyboardProc (מבנה ה-callback)**  
    [https://learn.microsoft.com/windows/win32/winmsg/lowlevelkeyboardproc](https://learn.microsoft.com/windows/win32/winmsg/lowlevelkeyboardproc)
    
- **MSG Struct** (תור הודעות)  
    [https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-msg](https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-msg)
    
- **Virtual-Key Codes** (ערכי ‎`vkCode`)  
    [https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes](https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes)

---

## 📖 סיפור הדרך

- השלב הראשון הוא **אתחול וקישור ל־Windows API**. אני טוען את `user32.dll` דרך ‎`ctypes` ומגדיר לכל פונקציה את החתימות (`argtypes`/`restype`) – `GetWindowText*`, `GetKeyState`, `GetKeyboardState`, `ToAscii`, `SetWindowsHookExA`, `CallNextHookEx`, `GetMessageA`. במקביל אני מגדיר קבועים (`WH_KEYBOARD_LL`, `WM_KEYDOWN`, `WM_RETURN`, `WM_SHIFT`) ואת המבנה ‎`KBDLLHOOKSTRUCT` שמייצג אירוע מקלדת נמוך־רמה.
    
- אחר כך אני מגדיר את **טיפוס ה־callback בסגנון C**:  
    `HOOKPROC = CFUNCTYPE(LRESULT, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)`.  
    זה “מתרגם” לפייתון את החתימה ש־Windows דורשת: `LRESULT CALLBACK(int nCode, WPARAM wParam, LPARAM lParam)`. בהמשך אעטוף את `hook_function` ב־`HOOKPROC` כדי שה־OS יוכל לקרוא אליה כאילו הייתה פונקציית C.
    
- כעת אני יוצר **פונקציה לזיהוי החלון שבפוקוס** – `get_foreground_process`:  
    קורא ל־`GetForegroundWindow` כדי לקבל `HWND` של החלון הפעיל → מחשב את אורך הכותרת עם `GetWindowTextLengthA` → מקצה buffer בגודל ‎`length+1` (כולל `\0`) → ממלא את הטקסט עם `GetWindowTextA` ומחזיר את המחרוזת. כך אני מתייג כל הקשה לפי הכותרת של החלון הפעיל באותו רגע.
    
- אני **עוטף את פונקציית ה־Python** שלי כ־callback תואם WinAPI:  
    `callback = HOOKPROC(hook_function)`.  
    מכאן Windows יכולה לזמן את `hook_function` דרך המתאם של `ctypes`.
    
- אני **מתקין Hook למקלדת**:  
    `hook = SetWindowsHookExA(WH_KEYBOARD_LL, callback, 0, 0)`.  
    זה רושם הוק גלובלי נמוך־רמה ללחיצות מקלדת (מותר `hMod=NULL, dwThreadId=0` עבור LL-hook). הערך המוחזר (`hook`) הוא ה־handle להוק.
    
- אני מפעיל **לולאת הודעות** כדי להשאיר את הת’רד “חי”:  
    `GetMessageA(byref(wintypes.MSG()), 0, 0, 0)`.  
    הקריאה הזו לא “מזמינה” את ה־hook ידנית – היא פשוט מחזיקה message queue פעיל כך של־Windows יהיה לאן למסור אירועים. אידיאלית זה רץ בלולאה (`while GetMessageA(...): ...`), אבל גם קריאה חוסמת אחת שומרת את התהליך חי עד שתגיע הודעת סיום.
    
- בתוך **`hook_function`** מתבצע הטיפול באירועים:  
    בכל אירוע, אם כותרת החלון השתנתה – אני מדפיס header עם שם החלון (קונטקסט). אם `wParam == WM_KEYDOWN`, אני יוצר `KBDLLHOOKSTRUCT` מתוך ה־`lParam` כדי לגשת ל־`vkCode/scanCode`, מעדכן תמונת מצב של המקלדת עם `GetKeyState(WM_SHIFT)` ו־`GetKeyboardState(state)`, ואז מנסה למפות לתו בעזרת `ToAscii(vkCode, scanCode, state, buf, 0)`. אם `n > 0`: אם זה `WM_RETURN` – ירידת שורה; אחרת אני מדפיס את התו (ללא ירידת שורה, עם `flush=True`).
    
- בסוף כל אירוע אני **מעביר את השרביט הלאה**:  
    `return CallNextHookEx(hook, nCode, wParam, lParam)` – כך איני חוסם את שרשרת ההוקים והאירוע ממשיך ליעדו (למשל לדפדפן/אפליקציה שבפוקוס).

---

## חידודי־מפתח

- **למה צריך `HOOKPROC = CFUNCTYPE(...)`?**  
    כדי להגדיר _טיפוס פונקציה בסגנון C_ עם אותה חתימה ש־Windows מצפה לה. אחר כך `callback = HOOKPROC(hook_function)` עוטף את `hook_function` כך שה־OS יוכל לזמן אותה.

- **מה עושה `GetMessageA(byref(MSG), 0, 0, 0)` בשורה הסופית?**  
    זו משיכת הודעות מה־message queue והחזקת הלולאה “בחיים”. בלי message loop פעיל, ה־thread שמתקין את ההוק היה נסגר, וההוק היה מתבטל.

- **איך `GetMessageA` מתחבר ל־`hook_function`?**  
    החיבור נוצר כבר ב־`SetWindowsHookExA(WH_KEYBOARD_LL, callback, 0, 0)`. מרגע הרישום, **Windows** היא זו שקוראת ל־`callback` שלך על כל אירוע מקלדת רלוונטי.

- **שלוש השורות הקריטיות**:  
    • `callback = HOOKPROC(hook_function)` – עטיפה לפונקציית Python לטיפוס C תואם WinAPI.  
    • `hook = SetWindowsHookExA(WH_KEYBOARD_LL, callback, 0, 0)` – רישום ההוק.  
    • `GetMessageA(byref(wintypes.MSG()), 0, 0, 0)` – מחזיק את ה־thread חי עם message queue.

---

## 🔄 זרימת הפעולות

[משתמש לוחץ מקש]  
← Windows יוצרת אירוע מקלדת  
← GetMessageA קולט את ההודעה מתור ההודעות  
← ההודעה נשלחת ל־hook_function (דרך ה־callback)  
← hook_function בודקת אם wParam == WM_KEYDOWN  
← אם כן → בונים struct מסוג KBDLLHOOKSTRUCT מ־lParam  
← הפונקציה קוראת ל־get_foreground_process כדי לדעת מהו החלון הפעיל  
← GetKeyState(WM_SHIFT) בודקת אם Shift לחוץ  
← GetKeyboardState(state) ממלאת את כל מצב המקשים במערך של 256 ערכים  
← ToAscii(vkCode, scanCode, state, buf, 0) מתרגם את ההקשה לתו ASCII  
← אם n > 0 → הצלחנו להמיר לתו  
← אם vkCode == WM_RETURN → מבצעים ירידת שורה  
← אחרת → string_at(buf).decode("latin-1") מחזיר את התו הרגיל להדפסה  
← print(..., end="", flush=True) מציג את התו על המסך בלי לרדת שורה  
← CallNextHookEx שולח את האירוע הלאה  
← החלון המקורי (למשל Chrome) מקבל את ההקשה בפועל

---

> הערה: עבודה עם hooks ברמת מערכת היא יכולת רגישה. חובה להשתמש בזה בצורה חוקית, אתית ומבוקרת בלבד.
