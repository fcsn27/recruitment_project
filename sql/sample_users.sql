-- Insert initial user data into accounts_customuser
INSERT INTO accounts_customuser (
    id, password, last_login, is_superuser, username, email, full_name, phone, address, 
    is_active, is_staff, role, date_joined
) VALUES
    -- HR user (id=1)
    (1, 'pbkdf2_sha256$870000$randomsalt$2bY5QzI3g8eJ3o5L7kM9zX5pQv2nW6iR9tY8uZ3vA7w=', NULL, 0, 'hr_user', 'hr@example.com', 'HR Manager', '1234567891', '123 HR Street', 1, 1, 'hr', '2025-05-16 15:05:00'),
    -- Applicant user (id=2)
    (2, 'pbkdf2_sha256$870000$randomsalt$8cX4PzK2h7fI2n4M6jL8yW4oQu1mV5hS8sX7tY2uA6v=', NULL, 0, 'applicant_user', 'applicant@example.com', 'Applicant User', '1234567890', '123 Applicant Street', 1, 0, 'applicant', '2025-05-16 15:05:00'),
    -- Director user (id=3)
    (3, 'pbkdf2_sha256$870000$randomsalt$9dZ5QyL3i8gJ3p5N7kM9xX5pRv2nW6iT9tY8uZ3vB8w=', NULL, 0, 'director_user', 'director@example.com', 'Company Director', '1234567892', '123 Director Street', 1, 1, 'director', '2025-05-16 15:05:00'),
    -- Department user (id=4)
    (4, 'pbkdf2_sha256$870000$randomsalt$7bW4PzM2h7fI2n4L6jK8yV4oPu1mU5hR8sW7tX2uA5v=', NULL, 0, 'department_user', 'department@example.com', 'Department Manager', '1234567893', '123 Department Street', 1, 0, 'department', '2025-05-16 15:05:00');