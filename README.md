# EDA Storage Renting Site

This project is an **EDA (Event-Driven Architecture)** based storage-unit renting platform. The timeline for this project was 7 business days, from scratch. 
Users can rent storage units, browse available spaces, and manage their renting accounts efficiently through an online portal. The backend is built using a microservice architecture that follows event-driven principles, ensuring scalability and high responsiveness. The requests are handled by a REST API.

## Table of Contents
- [Backend Architecture](#backend-architecture)
- [Frontend](#frontend)
  - [Screenshots](#screenshots)
- [Technologies Used](#technologies-used)
- [Installation Guide](#installation-guide)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [License](#license)

## Backend Architecture

The backend architecture of this project follows an **Event-Driven** design to ensure that different components of the system are decoupled and can react to changes or events in real-time. Here's an overview of the system:
    - REST API
        -> /rent                       - Used to rent a unit
        -> /create_user                - Used to create a user 
        -> /units                      - Used to access and change unit information
        -> /notifications              - Used to get the notifications from a specific unit

![Backend Architecture Diagram](Screenshots/architecture-diagram.png) <!-- Replace with a link to your diagram -->

## Frontend

The frontend is designed with a user-friendly interface that lets customers browse storage units, make bookings, and manage their rental accounts.

### Screenshots:

#### Home Page
![Home Page](Screenshots/HomePage.png) <!-- Replace with a screenshot of the homepage -->

#### Storage Units Rented by Current User
![RentedUnits](Screenshots/RentedUnits.png) <!-- Replace with a screenshot of the browsing page -->

#### Unit Details
![Unit Details](Screenshots/UnitDetails.png) <!-- Replace with a screenshot of the user profile page -->

#### Notifications Page
![Notifications Page](Screenshots/NotificationsPage.png) <!-- Replace with a screenshot of the user profile page -->

#### Search Available Units
![Search Available Units](Screenshots/SearchAvailableUnits.png) <!-- Replace with a screenshot of the checkout page -->

#### Search Result of Available Units
![Search Result of Available Units](Screenshots/SearchAvailableUnits.png)


## Technologies Used

- **Backend**:
  - REST API (AWS API Gateway)
  - Microservices (AWS Lambda)
  - AWS DynamoDB (for non-relational data storage)
  - AWS CloudFront (for caching)
  - JWT (for user authentication)

- **Frontend**:
  - HTML & CSS (for UI)
  - Java Script (for frontend logic)

- **DevOps**:
  - AWS SAM (for Infrastructure as Code)

## Installation Guide

To run the project locally, follow the steps below.

### Prerequisites:
- AWS SAM CLI
- AWS Account

### Step 1: Clone the repository

```bash
git clone https://github.com/ShaneDCarr/SpareRoom.git
cd SpareRoom
```

### Step 2: Install requirements

```bash
pip intall -r requirements.txt
```

### Step 3: Initialise the build

```bash
sam build
```


### Step 4: Intialise the Deployment

```bash
sam deploy --guided
```

### Step 5: Fill The Bucket

```
    - Go to your stack on cloud formation
    - In your Outputs, you will find a link to your S3 bucket
    - Upload everyting in the src/frontend folder to your bucket
```

### Step 6: Visit your website

```
    - Go to your stack on cloud formation
    - In your Outputs, you will find a link to the site hosted on your S3 bucket
```
