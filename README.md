
# Timesheet Program

A Python-based timesheet management application designed to streamline employee attendance tracking and administrative tasks.

# Screenshots
![image](https://github.com/user-attachments/assets/e7a9744c-c16b-49d8-848d-a82776dec539)




![image](https://github.com/user-attachments/assets/c3a9a6d7-76f6-47a8-9725-2b13721b23e1)



## 📋 Features

- **Clock-In System**: Record employee check-ins and check-outs efficiently.
- **Database Management**: Utilizes SQLite databases (`OFFICE.db`, `identifier.sqlite`) for storing and managing timesheet data.
- **Configuration**: Customizable settings via `config.yaml`.
- **Audio Notifications**: Incorporates `login.wav` for auditory alerts.
- **User Interface**: Accessible through HTML pages located in the `pages/` directory.
- **Branding**: Features company branding with `wieconLogo.png`.
- **Creation of new admin and login page**: using a third-party plugin [Streamlit-Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator) to create a login page to login into the admin page and within the admin page the creation of new admin which the CEO of the compnay has access



## 🚀 Usage

3. **Access the Interface**:

   Open the HTML files located in the `pages/` directory using a web browser to interact with the application's user interface.

## 📁 Project Structure

```plaintext
timesheetProgram/
├── .devcontainer/           # Development container configurations
├── .idea/                   # IDE-specific settings (e.g., PyCharm)
├── pages/                   # HTML pages for the user interface
├── OFFICE.db                # Primary SQLite database for timesheet records
├── identifier.sqlite        # Secondary SQLite database for user identification
├── clockInSystem.py         # Main application script
├── databaseManagement.py    # Handles database operations
├── Sample.py                # Sample script or testing module
├── config.yaml              # Configuration file
├── login.wav                # Audio file for login notifications
├── wieconLogo.png           # Company logo image
├── golden-gate-bridge.png   # Decorative image used in the README
└── requirements.txt         # Python dependencies
```

## ✅ Requirements

- Python 3.6 or higher
- Operating System: Windows, macOS, or Linux
- SQLite3
- Web Browser (for accessing HTML pages)

## 📌 Notes

- Ensure that the `OFFICE.db` and `identifier.sqlite` databases are properly initialized before running the application.
- The `login.wav` file should be placed in the root directory to enable audio notifications.
- Customize the HTML pages in the `pages/` directory to match your organization's branding and requirements.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
