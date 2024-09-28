# TODO

## Backend
- [ ] Test API
    - [ ] Create API collection
    - [ ] Test all requests
        - [ ] Book requests
            - [ ] Create new book
            - [ ] Show all books
                - [ ] Fix bug where types shown are always the same as the first in the list
            - [ ] Show specific book
                - [ ] Fix bug where types shown are always the same as the first in the list
            - [ ] Update a book
            - [ ] Delete a book
        - [ ] Book types requests
            - [ ] Show all book types
            - [ ] show specific book type
        - [ ] Customer requests
            - [ ] Create customer
            - [ ] Show all customers
            - [ ] Show specific customer
            - [ ] Delete customer
        - [ ] Loans requests
            - [ ] Create a loan
            - [ ] Show all loans
            - [ ] Show specific loan
            - [ ] Update a loan
            - [ ] Delete a loan
- [ ] Add parameters to the requests
    - [ ] Add show hidden boolean parameter to the get requests
- [ ] Add bulk requests
    - [ ] Bulk upload of books
    - [ ] Bulk delete of books
    - [ ] Bulk upload of customers
    - [ ] Bulk delete of customers
    - [ ] Bulk upload of loans
    - [ ] Bulk delete of loans
- [ ] Add function to show remaining loan time (or days overdue)
- [ ] Add a queue feature for loans
    - [ ] Add a new model named loans_queue with a relationship to the books and customers models
    - [ ] Correct the create loan function so that if a book is already loaned, it adds the user to the books loan queue
    - [ ] Create a return book function
        - [ ] Add a column for the date a book was actually returned and differentiate it with the expected return date of the book
        - [ ] Add a funtion to return the book which will provide an actual return date for the book and create a loan for the next customer in the queue for the book
- [ ] Add a request more time function that has to be approved and updated by an admin
- [ ] Create a login system for the app
    - [ ] Create a profiles model with a relationship to the customers model
    - [ ] Create a token system (saved in cookies)
    - [ ] Create a register function
    - [ ] Implement the token system in the API
    - [ ] Update the API collection after the changes
    - [ ] Test the API again

## Frontend

