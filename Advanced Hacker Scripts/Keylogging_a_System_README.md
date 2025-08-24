# Keylogging a System (Windows API Demo)

⚠️ שימוש ב-Keylogging מותר אך ורק בסביבות מעבדה/מחקר ועל מערכות שבהן יש לך הרשאה מפורשת.  
המדריך הזה מתאר את המבנה הלימודי-טכני של הסקריפט בלבד.

---

## שלבי העבודה

### 1. אתחול וקישור ל־Windows API
אני טוען את `user32.dll` דרך ‎`ctypes` ומגדיר לכל פונקציה את החתימות (`argtypes`/`restype`) –  
**[GetWindowTextA](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowtexta)**,  
**[GetKeyState](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getkeystate)**,  
**[GetKeyboardState](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getkeyboardstate)**,  
**[ToAscii](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-toascii)**,  
**[SetWindowsHookExA](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowshookexa)**,  
**[CallNextHookEx](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-callnexthookex)**,  
**[GetMessageA](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getmessagea)**.  

במקביל אני מגדיר קבועים (`WH_KEYBOARD_LL`, `WM_KEYDOWN`, `WM_RETURN`, `WM_SHIFT`) ואת המבנה ‎`KBDLLHOOKSTRUCT`.

### 2. הגדרת טיפוס callback
אני מגדיר:  
```python
HOOKPROC = CFUNCTYPE(LRESULT, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)
```  
זה מתאר ל־Windows את החתימה הנדרשת:  
`LRESULT CALLBACK(int nCode, WPARAM wParam, LPARAM lParam)`  
ומאפשר לי לעטוף את `hook_function` כך שתתפקד כפונקציה בסגנון C.

### 3. זיהוי חלון בפוקוס
אני יוצר פונקציה `get_foreground_process`:  
משתמש ב־**[GetForegroundWindow](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getforegroundwindow)** כדי לקבל HWND,  
בודק את אורך הכותרת עם **[GetWindowTextLengthA](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowtextlengtha)**,  
מקצה buffer, ממלא עם **[GetWindowTextA](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowtexta)** ומחזיר מחרוזת.  
ככה אני יודע בכל הקשה באיזה חלון המשתמש נמצא.

### 4. עטיפת הפונקציה
אני עוטף את `hook_function` עם `HOOKPROC` ומייצר `callback` –  
מכאן Windows יכולה לזמן את הקוד שלי בכל אירוע מקלדת.

### 5. התקנת Hook
אני קורא ל־**[SetWindowsHookExA](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowshookexa)** עם `WH_KEYBOARD_LL` כדי להתקין hook גלובלי ללכידת הקשות.  
הפונקציה מחזירה handle (`hook`) שמייצג את ההוק.

### 6. לולאת הודעות
אני מפעיל את **[GetMessageA](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getmessagea)** כדי להחזיק message loop חי.  
בלי זה, ההוק היה מתבטל ברגע שהת’רד מסתיים.

### 7. טיפול בהקשות
בכל פעם ש־Windows שולחת אירוע:  
- אם הכותרת השתנתה → אני מדפיס header חדש.  
- אם `WM_KEYDOWN` → אני בונה `KBDLLHOOKSTRUCT`, בודק מצב מקשים עם **[GetKeyState](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getkeystate)** ו־**[GetKeyboardState](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getkeyboardstate)**,  
ואז ממיר את ה־vkCode ל־ASCII בעזרת **[ToAscii](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-toascii)**.  
אם ההמרה הצליחה (`n > 0`):  
  - אם זה Enter → ירידת שורה.  
  - אחרת → אני מדפיס את התו.

### 8. שחרור האירוע
בכל סוף קריאה אני מפעיל **[CallNextHookEx](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-callnexthookex)** כדי לא לחסום את האירוע ומאפשר לו להמשיך לאפליקציה היעד.

---

## נקודות מעניינות

- **HOOKPROC** – מתרגם בין Python ל־WinAPI.  
- **GetMessageA** – לא מזמינה את ה־hook בעצמה, אלא משאירה את התהליך חי כדי ש־Windows תוכל לשלוח אירועים.  
- **ToAscii** – פונקציה מיושנת אך מספיקה לצורך הדגמה; בגרסאות מתקדמות משתמשים ב־ToUnicodeEx.  
- **שקיפות** – בזכות `CallNextHookEx`, האפליקציה עדיין מקבלת את ההקשות שלה.

---

## סיכום
הסקריפט מתקין **Low-Level Keyboard Hook**, מזהה את החלון שבפוקוס, מתעד את כל ההקשות (כולל תרגום לתווים), ושומר על רצף עבודה של המערכת.  
כך ניתן להדגים בצורה חינוכית איך Windows Hooks עובדים ברמת מערכת.
