@echo off
cd /d %~dp0
call .venv\Scripts\activate
streamlit run turnos_tareas_seguimientos.py
pause
