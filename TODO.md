# TODO

## Backend
- [x] Implement a migrations system __(alembic module)__ to make changes on the database structure _29/09/2024_
- [ ] Test API
    - [x] Create API collection
    - [ ] Test all requests
        - [x] Book requests
            - [x] Create new book - _28/09/2024_
            - [x] Show all books - _28/09/2024_
                - [x] Fix bug where types shown are always the same as the first in the list - _28/09/2024_
            - [x] Show specific book - _28/09/2024_
                - [x] Fix bug where types shown are always the same as the first in the list - 28/09/2024
            - [x] Update a book - _28/09/2024_
            - [x] Delete a book - _28/09/2024_
        - [x] Book types requests - _28/09/2024_
            - [x] Show all book types - _28/09/2024_
            - [x] show specific book type - _28/09/2024_
        - [x] User requests _02/10/2024_
            - [x] Create user _02/10/2024_
            - [x] Show all users _02/10/2024_
            - [x] Show specific user _02/10/2024_
            - [x] Delete user _02/10/2024_
        - [ ] Loans requests
            - [ ] Create a loan
            - [ ] Show all loans
            - [ ] Show specific loan
            - [ ] Update a loan
            - [ ] Delete a loan
- [x] Add parameters to the requests
    - [x] Add show hidden boolean parameter to the get 
        - [x] Add the parameter to the book get requests - _28/09/2024_
        - [x] Add the parameter to the users get requests
    - [x] Add show only hidden boolean parameter to the get
        - [x] Add the parameter to the book get requests - _28/09/2024_
        - [x] Add the parameter to the users get requests
    requests _02/10/2024_
- [x] Add bulk requests
    - [x] Bulk upload of books _30/09/2024_
    - [x] Bulk delete of books _02/10/2024_
    - [x] Bulk upload of users _30/09/2024_
    - [x] Bulk delete of users _02/10/2024_
    - [x] Bulk upload of loans _02/10/2024_
    - [x] Bulk delete of loans _02/10/2024_

- [x] Have certain functions be allowed only for admin or superadmin profiles _02/10/2024_
- [x] add cities as a separate model with static values (prestored in a json file) automatically added to the database (if empty) on app launch _02/10/2024_
- [x] add categories as a separate model with static values (prestored in a json file) automatically added to the database (if empty) on app launch _02/10/2024_
- [ ] Add function to show remaining loan time (or days overdue)
- [ ] Add a queue feature for loans
    - [ ] Add a new model named loans_queue with a relationship to the books and users models
    - [ ] Correct the create loan function so that if a book is already loaned, it adds the user to the books loan queue
    - [ ] Create a return book function
        - [ ] Add a column for the date a book was actually returned and differentiate it with the expected return date of the book
        - [ ] Add a funtion to return the book which will provide an actual return date for the book and create a loan for the next user in the queue for the book
- [ ] Add a request more time function that has to be approved and updated by an admin
- [ ] Create a login system for the app
    - [x] Create a profiles model with a relationship to the users model _30/09/2024_
    - [x] Create a token system _01/10/2024_
    - [x] Create a register function _01/10/2024_
    - [x] Implement the token system in the API _01/10/2024_
    - [x] Update the API collection after the changes _02/10/2024_
    - [x] Test the API again _02/10/2024_
- [ ] Add a folder with examples to the api collection so that on first app run you can easily create multiple entries on all models
- [ ] Implement a function to recover a forgotten password
- [ ] Find an easy way to get book cover images (maybe a free API or book cover image database) and implement it

## Frontend

- [ ] Research examples of existing websites
- [ ] Write a plan for the website
- [ ] Find visual assets
    - [ ] Logo
    - [ ] Background images
    - [ ] Favicon
    - [ ] Extra images


## README File

- [ ] write an elaborate and detailed README file

## Finishing touches
- [ ] Update the requirements.txt file and make sure all necessary modules and versions are included