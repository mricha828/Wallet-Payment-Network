CREATE TABLE
    BANK_ACCOUNT(
        BANK_ID int NOT NULL,
        BANK_NUMBER int NOT NULL,
        Constraint pk1 PRIMARY KEY(BANK_ID, BANK_NUMBER)
        )