# Use cases

## A simple web service

The basic use case for gotcha-system is protecting a server offering service through the Web.

Let's suppose that the service consists of a document (like a manifesto) such that

- any user on the Web can **read** the document
- only some users (*priviledged users*) can **edit** the document

The goal of gotcha-system is to detect suspicious activity from users using the service to support the security team in their investigative work.

In this case, suspicious activity may include

- A priviledged user performs action in a time of the day that outside from their normal time range. 
- A priviledged user logs in with a IP different than usual
- Too many edits in a short amount of time
- Too many priviledged users logging in
- Two consecutive logins from same user (i.e. not a logout in between)
- Failed requests (es. failed login)
