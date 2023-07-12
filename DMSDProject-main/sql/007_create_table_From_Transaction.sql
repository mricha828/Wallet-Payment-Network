CREATE TABLE
    FROM_TRANSACTION(
        RT_ID int,
        IDENTIFIER VARCHAR(20) not null,
        PERCENT_CUT int(10) DEFAULT(100) not null,
        CONSTRAINT FK_FROM_IDENTIFIER FOREIGN kEY(IDENTIFIER) REFERENCES ELEC_ADDRESS(IDENTIFIER) ON UPDATE CASCADE
        ON DELETE CASCADE,
        CONSTRAINT FK_FROM_RT_ID FOREIGN kEY(RT_ID) REFERENCES REQUEST_TRANSACTION(RT_ID) ON UPDATE CASCADE
        ON DELETE CASCADE
    )