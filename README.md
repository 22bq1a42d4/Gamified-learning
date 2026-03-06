# Gamified Learning Platform...

## 📌 Project Overview
The **Gamified Learning Platform with Hierarchical Monitoring System** is an educational web application designed to improve student engagement through gamification techniques such as points, badges, leaderboards, and progress tracking.

The platform aims to support students, especially in rural areas, by providing an interactive learning environment while allowing teachers and administrators to monitor student progress through a hierarchical monitoring system.

---

## 🎯 Objectives
- Improve student engagement through gamified learning.
- Provide an interactive digital learning environment.
- Enable teachers to monitor and evaluate student performance.
- Support educational development in rural areas.

---

## ✨ Key Features
- 🎮 Gamified learning modules
- 📊 Student progress tracking
- 🏆 Points, badges, and leaderboard system
- 👨‍🏫 Teacher dashboard
- 🏫 Hierarchical monitoring system
- 📚 Interactive quizzes and learning activities
- 🔐 User authentication
- 📈 Performance analytics

---

## 🏗 System Architecture
The system follows a hierarchical architecture with three levels:

### Student Layer
- Access learning modules
- Complete quizzes and activities
- Earn points and rewards

### Teacher Layer
- Monitor student performance
- Assign learning tasks
- Evaluate progress

### Admin Layer
- Manage users and courses
- Monitor system activity
- Generate reports

---

## 💻 Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Django

### Database
- SQLite / MySQL

### Tools
- Git
- GitHub
- VS Code

---

## 📂 Project Structure

```
Gamified-learning
│
├── gamified_project/
│   │
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── learning_app/
│   │
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   │
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── db.sqlite3
├── manage.py
├── req.txt
└── README.md
```

---

## ⚙️ Installation and Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/22bq1a42d4/Gamified-learning.git
```

### 2️⃣ Navigate to the project directory
```bash
cd Gamified-learning
```

### 3️⃣ Create a virtual environment
```bash
python -m venv venv
```

### 4️⃣ Activate the virtual environment

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 5️⃣ Install dependencies
```bash
pip install -r req.txt
```

### 6️⃣ Apply database migrations
```bash
python manage.py migrate
```

### 7️⃣ Run the development server
```bash
python manage.py runserver
```

Open your browser and visit:

```
http://127.0.0.1:8000/
```

---

## 📊 Expected Outcomes
- Increased student engagement through gamified learning.
- Better monitoring of student progress.
- Improved accessibility to learning resources.
- Enhanced digital education for rural students.

---

## 👨‍💻 Team Members
- S. Naga Tejaswi  
- S. Abhinav Sahat  
- P. Noel  
- Sk. Imran  

---

## ⭐ Future Enhancements
- AI-based personalized learning
- Mobile application integration
- Offline learning support
- Advanced analytics and dashboards

---

## 📜 License
This project is developed for **academic and research purposes**.
