---
layout: page
title: Databases
subtitle: Artifact 03 · Databases
permalink: /artifacts/databases/
---

The Contact Service from [Artifact 1]({% link artifacts/software-design.markdown %}), moved to MongoDB with user logins and roles.
{: .lead}

[Original Java code]({{ site.repo_url }}/tree/gh-pages/artifacts/contact-service/original)
[Enhanced Python code]({{ site.repo_url }}/tree/gh-pages/artifacts/contact-service/enhanced)
[Download zip]({{ "/assets/downloads/contact-service.zip" | relative_url }})
{: .actions}

## Narrative

The artifact I selected for this enhancement is the Contact Service from CS-320. The original application was written in Java, and during my capstone work I recreated it in Python. The Python version originally stored contacts in memory, which meant the data was lost when the application closed. For this milestone, I expanded the project to use MongoDB so contacts and user accounts could be stored between sessions. I kept the original in-memory service as well so its existing functionality and tests would continue to work.

I included this artifact in my ePortfolio because it shows how I can take an existing application and improve it while preserving its main purpose. The enhancement demonstrates skills in database integration, application design, validation, testing, and security. I added a MongoDB service for contact operations, environment-based database configuration, and a login system with admin, editor, and viewer roles. I also improved how the application handles invalid input and database errors. For example, updates are validated before being saved so a failed update does not leave a contact only partially changed. The application also assigns contact IDs automatically while keeping them compatible with the original project’s ID length requirement.

The planned enhancement helped me make progress toward the course outcomes related to implementing computing solutions and developing a security mindset. Connecting the application to MongoDB gave me practical experience with persistent data, while authentication and role-based permissions helped me think about who should be allowed to access or change information. I also improved the project’s documentation and added tests to demonstrate that the changes work. My plans for outcome coverage have not changed, but this enhancement gives me stronger evidence for database development and security. I still see room to improve the project, especially around more advanced account management and production database security.

One of the biggest lessons from this process was that adding a database involves more than replacing a dictionary with a database collection. I had to consider connection failures, duplicate IDs, validation, permissions, and how to keep the existing functionality working. Keeping the original in-memory ContactService and adding a separate MongoDB service allowed me to preserve the original tests while introducing the new functionality. I also used mongomock and mocks to test database behavior without requiring a live server for every automated test.

Testing was an important part of the enhancement. The project finished with 75 automated tests passing, including the original tests and new tests for MongoDB operations, authentication, permissions, and database errors. I also manually checked the application against a local MongoDB server to confirm that data remained available after restarting the application and that users with different roles had different permissions. One challenge was making errors clear without exposing unnecessary information or allowing invalid input to reach the database. Working through these issues helped me understand why validation and security need to be considered throughout development, rather than added only after the main features are finished. Overall, this enhancement gave me more experience building an application that is persistent, testable, and safer to use

## Roles

| Role   | Add | View | Update | Delete | Add users |
|--------|-----|------|--------|--------|-----------|
| admin  | yes | yes  | yes    | yes    | yes       |
| editor | yes | yes  | yes    | no     | no        |
| viewer | no  | yes  | no     | no     | no        |

## Pseudocode

Planned before the enhancement:

```text
START
Connect to MongoDB
IF the database does not exist
    Create database and contact collection
END IF
User logs in
Check user permissions
IF user has permission
    Allow access to contact list
    IF user adds a contact
        Insert contact into MongoDB
    ELSE IF user updates a contact
        Update contact in MongoDB
    ELSE IF user deletes a contact
        Delete contact from MongoDB
    ELSE IF user views contacts
        Retrieve contacts from MongoDB
    END IF
ELSE
    Deny access
END IF
Close database connection
END
```

The [README]({{ site.repo_url }}/blob/gh-pages/artifacts/contact-service/enhanced/README.md) explains how to set up MongoDB, run the program, and run the tests.
