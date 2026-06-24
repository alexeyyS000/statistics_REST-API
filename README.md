# Statistics REST API

A service for collecting survey data and city updates from the Moscow Active Citizen platform (`ag.mos.ru`) and providing statistical information through a REST API.

## Technologies

* Django REST Framework (DRF)
* Playwright
* Celery
* Docker
* PostgreSQL
* RabbitMQ
* Stripe

## Implemented Features

* Developed a REST API for accessing and analyzing collected statistics;
* Implemented JWT-based authentication and authorization;
* Integrated Stripe for subscription plan payments;
* Built a web scraping service using Playwright for automated data collection;
* Implemented data processing and persistence in PostgreSQL;
* Configured asynchronous task execution with Celery and RabbitMQ;
* Containerized the application using Docker for easy deployment and scalability.
