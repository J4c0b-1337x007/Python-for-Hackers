# Process Creation & Shellcode Execution

הסקריפט הזה הוא מבחינתי הדגמה קלאסית ל־**Process Creation & Shellcode Execution**.  
במקום להזריק DLL כמו בתרגיל הקודם, הפעם אני הולך צעד קדימה: אני יוצר תהליך חדש בעצמי (`notepad.exe`), עוצר אותו מייד עם הלידה שלו במצב **Suspended**, מזריק לתוכו **shellcode** מוכן (שהפקתי מראש עם `msfvenom`), משנה את ההרשאות של ה־memory כדי שיהיה **Executable**, ואז גורם ל־thread הראשי של התהליך להפעיל את ה־shellcode דרך **APC** (Asynchronous Procedure Call) וחידוש הThread הראשי.

---

## שלבי העבודה

### 1. הגדרות בסיסיות
אני מתחיל בהגדרות: טיפוסים כמו `SIZE_T = c_size_t`, `LPTSTR`, `LPBYTE`, וגם שני structs חשובים — `STARTUPINFO` ו־`PROCESS_INFORMATION`.  
הראשון קובע איך התהליך החדש יתחיל (חלון, flags), והשני מחזיר לי מידע על התהליך החדש שנוצר — ה־**hProcess**, ה־**hThread**, וגם ה־PID וה־TID.

### 2. יצירת התהליך
אני משתמש ב־**Windows API [`CreateProcessA`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa)**.  
נותן את הנתיב ל־`C:\Windows\System32\notepad.exe`, עם flags כמו `CREATE_SUSPENDED` ו־`CREATE_NO_WINDOW`.  
הפונקציה מחזירה לי handles לתהליך ול־thread שלו.

### 3. הקצאת זיכרון
בעזרת **Windows API [`VirtualAllocEx`](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex)**, אני מקצה בלוק בזיכרון של התהליך הזר בגודל ה־shellcode (`len(buf)`).  
הרשאות ראשוניות הן `PAGE_READWRITE`. הפונקציה מחזירה לי כתובת בזיכרון (`remote_memory`).

### 4. כתיבת shellcode
אני משתמש ב־**Windows API [`WriteProcessMemory`](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory)**.  
מעביר את ה־handle, הכתובת שקיבלתי, ואת הבייטים עצמם (`buf`). עכשיו ה־shellcode נמצא בתוך notepad.exe, מוכן להרצה.

### 5. שינוי הרשאות
עם **Windows API [`VirtualProtectEx`](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotectex)** אני משנה את ההרשאות ל־`PAGE_EXECUTE_READ`.  
כך ה־CPU מאפשר להריץ את הקוד. אני גם מקבל ערך של ההרשאות הישנות (`old_protection`).

### 6. הרצה – APC Injection
במקום ליצור thread חדש עם **Windows API [`CreateRemoteThread`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread)**, אני משתמש ב־**Windows API [`QueueUserAPC`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc)**.  
אני "מתזמן" את ההרצה של ה־shellcode ל־queue של ה־thread הראשי.  
אחר כך אני קורא ל־**Windows API [`ResumeThread`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread)** כדי לשחרר אותו מהקפאה. כשהוא מתעורר, הוא נכנס ל־alertable state ומריץ את ה־APC — שזה בעצם ה־shellcode.

---

## נקודות מעניינות

- **PAGE_EXECUTE רק בסוף** – קודם Write ואז Execute, כדי למזער סיכונים.  
- **oldProtection** – ערך הרשאות קודם (למשל `PAGE_READWRITE`) שאפשר לשחזר.  
- **למה APC?** – “שקט” יותר מ־CreateRemoteThread, כי אין thread חדש שנוצר.  
- **שגיאות** – כל קריאה עטופה ב־`verify(x)` שמחזירה **[`WinError`](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes)** במקרה כשלון.

---

## סיכום
צעד־צעד יצרתי תהליך Notepad מוקפא, החדרתי לתוכו shellcode, שיניתי הרשאות, הוספתי APC, ושחררתי את ה־thread.  
כשהוא קם – הוא פשוט התחיל להריץ את הקוד שלי.
