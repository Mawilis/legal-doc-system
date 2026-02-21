# Wilsy OS

[![Wilsy OS Global Pipeline](https://github.com/Mawilis/legal-doc-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Mawilis/legal-doc-system/actions/workflows/ci.yml)

Welcome to the **Legal Document System** repository! This project is designed to help legal professionals manage and collaborate on legal documents, while also providing role-based access control, real-time notifications, and secure communication over WebSockets.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

## Overview

The **Legal Document System** is a web-based application built to streamline the management of legal documents. The system supports user roles such as Admin, Attorney, and Sheriff, with each role having its specific permissions. Additionally, the app supports real-time notifications, document collaboration, and secure communications using HTTPS and WebSockets.

## Key Features

- **Role-Based Access Control (RBAC):** Admins, attorneys, and sheriffs have distinct roles and permissions.
- **Real-Time Notifications:** Get notifications for important events in real-time using WebSockets.
- **Document Management:** Create, edit, and manage legal documents easily.
- **Secure WebSockets:** All communications are secured using SSL certificates.
- **JWT Authentication:** Secure user authentication with JSON Web Tokens.
- **Push Notifications:** Send push notifications using VAPID and web push technology.

## Technologies Used

- **Frontend:** React, React Router, Styled Components
- **Backend:** Node.js, Express.js, MongoDB, Mongoose
- **Real-Time Communication:** Socket.io for WebSocket connections
- **Security:** HTTPS using SSL certificates, JWT for authentication, Helmet.js for security headers
- **Database:** MongoDB with Mongoose
- **Notifications:** Push notifications using Web Push and VAPID

## Project Structure

