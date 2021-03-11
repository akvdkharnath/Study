create table [user](
UserId int IDENTITY(1,1) PRIMARY KEY,
UserEmail varchar(100) not null,
UserPassword varchar(50) not null,
IsActive bit not null,
DateCreate datetime not null,
DateModified datetime,
IsProfileCreated bit not null 
)

ALTER TABLE [user] ADD CONSTRAINT df_IsProfileCreated DEFAULT 0 FOR IsProfileCreated
ALTER TABLE [user] ADD CONSTRAINT df_IsActive DEFAULT 0 FOR IsActive

go

create table [personalprofile](
ProfileId int IDENTITY(1,1) PRIMARY KEY,
UserId int not null,
FirstName varchar(50) not null,
MiddleName Varchar(50) ,
LastName varchar(50) not null,
DateOfBirth date,
Height float not null,
[Weight] float not null,
Sex varchar(10) not null,
Age tinyint not null,
BMIValue float not null,
BMICategory varchar(50) not null,
[Address] varchar(100) ,
PhoneNumber varchar(50),
MinWeight float,
MaxWeight float,
BMRValue float,
SuggestedBMRValue float,
[Message] varchar(100),
IsActive bit )

ALTER TABLE [personalprofile] ADD CONSTRAINT df_user_IsActive DEFAULT 0 FOR IsActive
ALTER TABLE [personalprofile] ADD CONSTRAINT FK_UserId FOREIGN KEY (UserId) REFERENCES [user](UserId);

go

create table [dashboard](
DashBoardId int IDENTITY(1,1) PRIMARY KEY,
UserId int not null,
IdealBMRValue float not null,
CalorieInput float not null,
CalorieOutput float not null,
Variation float not null,
[Date] date not null,
IsActive bit not null,
DateCreated datetime not null
)

ALTER TABLE [dashboard] ADD CONSTRAINT df_dashboard_IsActive DEFAULT 0 FOR IsActive
ALTER TABLE [personalprofile] ADD CONSTRAINT FK_dashboard_UserId FOREIGN KEY (UserId) REFERENCES [user](UserId)
