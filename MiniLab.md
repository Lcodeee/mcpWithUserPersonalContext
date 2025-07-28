# MiniLab - הוספת קריאת קבצים למערכת הזיכרון

## מטרת המעבדה
תוסיפו למערכת MCP יכולת לקרוא קבצי טקסט ולשמור את התוכן שלהם במסד הנתונים הוקטורי.

## דרישות מוקדמות
- Docker Desktop מותקן
- מפתח Gemini API
- עורך טקסט (VS Code מומלץ)

---

## שלב 1: הכנת הסביבה

### 1.1 Clone הפרויקט
```bash
git clone https://github.com/Lcodeee/mcpWithUserPersonalContext.git
cd mcpWithUserPersonalContext
cp .env.example .env
```

### 1.2 הגדרת מפתח API
ערכו את הקובץ `.env` והוסיפו את מפתח Gemini שלכם:
```env
LLM_API_KEY=your_gemini_api_key_here
```

### 1.3 בדיקת המערכת הבסיסית
```bash
docker-compose up -d
sleep 120  # המתינו 2 דקות לאתחול
docker-compose exec gemini_client python test_memory.py
```

**✅ ודאו שהמערכת עובדת לפני המשך!**

---

## שלב 2: יצירת תיקיית קבצים לבדיקה

### 2.1 צרו תיקיית test_files
```bash
mkdir test_files
```

### 2.2 צרו קבצי דוגמה
```bash
# קובץ על מתכונים
cat > test_files/recipes.txt << 'EOF'
מתכון לפסטה ברוטב עגבניות:
1. הרתיחו מים במחבת גדולה
2. הוסיפו פסטה ובשלו 8-10 דקות
3. הכינו רוטב עגבניות עם בזיליקום
4. ערבבו הכל והגישו חם
EOF

# קובץ על טכנולוגיה
cat > test_files/tech_notes.txt << 'EOF'
הערות על פיתוח תוכנה:
- Python הוא שפה מצוינת למתחילים
- Docker מפשט פריסת אפליקציות
- מסדי נתונים וקטוריים מאפשרים חיפוש סמנטי
- AI משנה את עולם הטכנולוגיה
EOF

# קובץ על נסיעות
cat > test_files/travel_diary.txt << 'EOF'
יומן נסיעות:
ביקרתי בפריז בקיץ האחרון. המגדל אייפל היה מרשים במיוחד בשקיעה.
המוזיאונים היו מלאי אמנות יפהפיה, במיוחד הלובר.
האוכל הצרפתי היה טעים - קרואסונים בבוקר וגבינות בערב.
EOF
```

---

## שלב 3: הוספת endpoint לקריאת קבצים

### 3.1 עריכת src/http_server.py
פתחו את הקובץ `src/http_server.py` והוסיפו את הפונקציה הבאה **לפני** השורה `if __name__ == "__main__"`:

```python
@app.post("/load_file")
async def load_file_endpoint(request: dict):
    """Load text from file and save to memory"""
    try:
        file_path = request.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")
        
        # בדיקה שהקובץ קיים
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        # קריאת הקובץ
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="File is empty")
        
        # שמירה בזיכרון עם מידע על המקור
        memory_text = f"[File: {file_path}]\n{content}"
        
        # שימוש בלקוח הזיכרון הקיים
        global mem0_client
        if mem0_client is None:
            mem0_client = get_mem0_client()
        
        result = mem0_client.add(memory_text, user_id="default_user")
        
        return {
            "success": True,
            "message": f"Successfully loaded file: {file_path}",
            "file_path": file_path,
            "content_length": len(content),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading file: {e}")
```

### 3.2 הוספת import נדרש
בתחילת הקובץ `src/http_server.py`, הוסיפו:
```python
import os
```

---

## שלב 4: יצירת סקריפט בדיקה

### 4.1 צרו קובץ test_file_loading.py
```python
#!/usr/bin/env python3
"""
Test script for file loading functionality
"""
import requests
import json
import os

def test_file_loading():
    print("🧪 Testing File Loading Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8050"
    
    # בדיקת בריאות השרת
    print("\n1. Testing server health...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print("❌ Server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # רשימת קבצים לבדיקה
    test_files = [
        "test_files/recipes.txt",
        "test_files/tech_notes.txt", 
        "test_files/travel_diary.txt"
    ]
    
    # טעינת קבצים
    print("\n2. Loading files into memory...")
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                response = requests.post(
                    f"{base_url}/load_file",
                    json={"file_path": file_path}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Loaded {file_path}")
                    print(f"   Content length: {result['content_length']} characters")
                else:
                    print(f"❌ Failed to load {file_path}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # בדיקת חיפוש
    print("\n3. Testing search functionality...")
    search_queries = [
        "איך מכינים פסטה?",
        "מה זה Docker?", 
        "איפה ביקרתי בחופשה?"
    ]
    
    for query in search_queries:
        try:
            response = requests.post(
                f"{base_url}/search_memories",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                memories = result.get('memories', [])
                print(f"\n🔍 Query: {query}")
                print(f"   Found {len(memories)} relevant memories:")
                for i, memory in enumerate(memories[:2], 1):  # הצגת 2 הראשונים
                    print(f"   {i}. {memory[:100]}...")
            else:
                print(f"❌ Search failed for: {query}")
                
        except Exception as e:
            print(f"❌ Search error for '{query}': {e}")
    
    print("\n" + "=" * 50)
    print("🎉 File loading test completed!")

if __name__ == "__main__":
    test_file_loading()
```

---

## שלב 5: הרצה ובדיקה

### 5.1 הפעלה מחדש של המערכת
```bash
# עצירת המערכת
docker-compose down

# הפעלה מחדש עם השינויים
docker-compose up -d

# המתנה לאתחול
sleep 120
```

### 5.2 הרצת הבדיקה
```bash
# העתקת סקריפט הבדיקה לקונטיינר
docker cp test_file_loading.py gemini_client:/app/

# הרצת הבדיקה
docker-compose exec gemini_client python test_file_loading.py
```

---

## שלב 6: בדיקות נוספות

### 6.1 בדיקה ידנית עם curl
```bash
# טעינת קובץ
curl -X POST http://localhost:8050/load_file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "test_files/recipes.txt"}'

# חיפוש
curl -X POST http://localhost:8050/search_memories \
  -H "Content-Type: application/json" \
  -d '{"query": "מתכון פסטה"}'
```

### 6.2 בדיקת כל הזיכרונות
```bash
curl http://localhost:8050/get_all_memories
```

---

## שלב 7: הרחבות אופציונליות

### 7.1 תמיכה בקבצי JSON
הוסיפו תמיכה בקריאת קבצי JSON:

```python
# הוסיפו לתחילת הפונקציה load_file_endpoint
import json as json_lib

# בתוך הפונקציה, אחרי קריאת הקובץ:
if file_path.endswith('.json'):
    try:
        data = json_lib.loads(content)
        content = json_lib.dumps(data, indent=2, ensure_ascii=False)
    except:
        pass  # אם זה לא JSON תקין, נשאיר כטקסט רגיל
```

### 7.2 הוספת מידע על תאריך
```python
from datetime import datetime

# בתוך הפונקציה:
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
memory_text = f"[File: {file_path}] [Loaded: {timestamp}]\n{content}"
```

### 7.3 יצירת endpoint לרשימת קבצים
```python
@app.get("/list_files")
async def list_files(directory: str = "test_files"):
    """List available files in directory"""
    try:
        if not os.path.exists(directory):
            return {"files": [], "message": f"Directory {directory} not found"}
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                files.append({
                    "name": file,
                    "path": file_path,
                    "size": os.path.getsize(file_path)
                })
        
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {e}")
```

---

## שלב 8: פתרון בעיות נפוצות

### בעיה: השרת לא מגיב
**פתרון:**
```bash
# בדיקת לוגים
docker-compose logs mcp_server

# הפעלה מחדש
docker-compose restart mcp_server
```

### בעיה: קובץ לא נמצא
**פתרון:**
- ודאו שהקובץ קיים: `ls -la test_files/`
- בדקו הרשאות: `chmod 644 test_files/*`

### בעיה: שגיאת encoding
**פתרון:**
```python
# שנו את קריאת הקובץ ל:
with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
    content = file.read()
```

---

## מה למדתם?

1. **הוספת API endpoints** למערכת קיימת
2. **קריאת קבצים** ב-Python
3. **שילוב עם מסד נתונים וקטורי** 
4. **בדיקת פונקציונליות** עם סקריפטים
5. **פתרון בעיות** במערכות מורכבות

## המשך מומלץ

- הוסיפו תמיכה בקבצי PDF
- צרו ממשק web לטעינת קבצים
- הוסיפו אימות משתמשים
- צרו מערכת תיוג לקבצים

**🎉 כל הכבוד! יצרתם מערכת זיכרון חכמה שיכולה לקרוא קבצים!**