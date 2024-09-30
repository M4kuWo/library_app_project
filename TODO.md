# TODO

## Backend
- [x] Implement a migrations system __(alembic module)__ to make changes on the database structure _29/09/2024_
- [ ] Test API
    - [ ] Create API collection
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
        - [ ] User requests
            - [ ] Create user
            - [ ] Show all users
            - [ ] Show specific user
            - [ ] Delete user
        - [ ] Loans requests
            - [ ] Create a loan
            - [ ] Show all loans
            - [ ] Show specific loan
            - [ ] Update a loan
            - [ ] Delete a loan
- [ ] Add parameters to the requests
    - [ ] Add show hidden boolean parameter to the get 
        - [x] Add the parameter to the book get requests - _28/09/2024_
        - [ ] Add the parameter to the users get requests
    - [ ] Add show only hidden boolean parameter to the get
        - [x] Add the parameter to the book get requests - _28/09/2024_
        - [ ] Add the parameter to the users get requests
    requests
- [ ] Add bulk requests
    - [x] Bulk upload of books _30/09/2024_
    - [ ] Bulk delete of books
    - [x] Bulk upload of users _30/09/2024_
    - [ ] Bulk delete of users
    - [ ] Bulk upload of loans
    - [ ] Bulk delete of loans
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
    - [ ] Create a token system (saved in cookies)
    - [ ] Create a register function
    - [ ] Implement the token system in the API
    - [ ] Update the API collection after the changes
    - [ ] Test the API again

## Frontend

