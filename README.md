# flask-jira-templates

Short notice: this is my first ever web app, no previous experience in such in any language; front-end experience is even  weeker ;)

Unfortunately this is not extension, but can be converted to it :) So here's short info what is the aim (flow) of this web app.

1. main feature is to create and save templates based on jira project's metadata and use the to fast create tickets in JIRA:
  1. using great [JIRA Python] (https://github.com/pycontribs/jira) library
  2. templates can be edited 
  3. templates are saved to database
  4. creating ticket with ability to resolve and add worklog in one go
  5. admin panel
2. integration with Active Directory:
  1. displaying interesting user's attributes (also as separate feature)
  2. required values are copied to template form
3. securing against jira unavailability: (feature not yet present)
  1. saving ready to create ticket in database
  2. info to user when they can be processed
4. securing against changes in JIRA project: (feature not yet present)
  1. synchronize saved jira templates against jira
  2. compare and update default templates (if possible)
  3. compare and update users templates (if possible)
  4. inform users about it
  
This is still work in progress, and as for today creating templates and tickets works. 
