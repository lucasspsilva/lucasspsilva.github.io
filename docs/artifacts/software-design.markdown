---
layout: page
title: Software Design
subtitle: Artifact 01 · Software Design and Engineering
permalink: /artifacts/software-design/
---

The Contact Service from CS 320, rewritten from Java to Python.
{: .lead}

[Original Java code]({{ site.repo_url }}/tree/gh-pages/artifacts/contact-service/original)
[Enhanced Python code]({{ site.repo_url }}/tree/gh-pages/artifacts/contact-service/enhanced)
[Download zip]({{ "/assets/downloads/contact-service.zip" | relative_url }})
{: .actions}

## Narrative

The artifact I selected is my final project from CS 320. It is a contact management application originally developed in Java. The application allows users to create, edit, delete, and manage contacts. I created the original artifact in October of 2024 as part of my CS 320 coursework.

I selected this artifact because it gives me a good opportunity to demonstrate my software development skills by taking an application I previously created and improving it using a different programming language. The original project demonstrates my experience with object-oriented programming, services, and testing. For this enhancement, I rewrote the application in Python while keeping the same main functionality. I also made the structure more Pythonic by using a dictionary to manage contacts and separated the contact model from the contact service. I added a terminal interface so the application can be used directly and created pytest tests to verify the functionality of the contact and contact service classes. I also added validation for situations such as duplicate contact IDs and invalid contact values. These changes allowed me to improve the original application while demonstrating that I can apply the same software requirements using a different language and development approach.

I believe I have made progress toward course outcome four, which focuses on using techniques, skills, and tools to implement computer solutions that deliver value. The Python rewrite demonstrates my ability to use a different programming language, testing tools, and software development practices to improve an existing application. I also made changes to the organization and validation of the original application rather than simply translating the Java code line by line. My outcome-coverage plan has not changed at this point. I plan to demonstrate additional outcomes through the algorithm and database enhancements later in the course.

The process of rewriting the artifact helped me understand that converting software to another language is more than changing the syntax. I had to consider how the same functionality should be implemented using Python conventions and structures. One of the challenges I faced was adapting the original Java service structure to Python while keeping the application easy to understand and test. I also learned more about using pytest and writing tests for different situations, including invalid input and duplicate contacts. Testing the application helped me find an error in how the service handled a null contact, which I was then able to correct. Overall, this enhancement helped me better understand how reviewing and improving existing software can be different from creating a project from the beginning.

## Program flow

![Flowchart: start, load contacts, user logs in, display options, then create, edit, or delete a contact and return to the options until the user exits]({{ "/assets/images/contact-service-flowchart.png" | relative_url }}){: .invert}

## About the posted code

The posted code also includes the MongoDB enhancement from [Artifact 3]({% link artifacts/databases.markdown %}). The in-memory version from this enhancement is still there, next to the MongoDB version:

- `contacts/contact.py`: the `Contact` class and its validation rules
- `contacts/contact_service.py`: the in-memory `ContactService`
- `main.py`: the terminal menu
- `tests/test_contact.py` and `tests/test_contact_service.py`: the pytest tests for both classes
