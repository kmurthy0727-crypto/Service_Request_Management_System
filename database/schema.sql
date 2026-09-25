USE service_request_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('service_coordinator', 'customer') NOT NULL
);

CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    status VARCHAR(50) DEFAULT 'available'
);

CREATE TABLE service_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    service_id INT NOT NULL,
    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',

    CONSTRAINT fk_request_user
        FOREIGN KEY (user_id) REFERENCES users(id),

    CONSTRAINT fk_request_service
        FOREIGN KEY (service_id) REFERENCES services(id)
);

CREATE TABLE service_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    service_id INT NOT NULL,
    completion_date DATETIME,
    status VARCHAR(50),

    CONSTRAINT fk_history_user
        FOREIGN KEY (user_id) REFERENCES users(id),

    CONSTRAINT fk_history_service
        FOREIGN KEY (service_id) REFERENCES services(id)
);