-- 创建数据库
CREATE DATABASE IF NOT EXISTS credit_card_assistant;

-- 使用数据库
USE credit_card_assistant;

-- 创建信用卡表
CREATE TABLE IF NOT EXISTS credit_cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    bank VARCHAR(50) NOT NULL,
    annual_fee TEXT,
    points_rule TEXT,
    benefits TEXT,
    card_type VARCHAR(50),
    credit_level VARCHAR(50),
    foreign_transaction_fee VARCHAR(50),
    card_organization VARCHAR(50),
    application_condition TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; 