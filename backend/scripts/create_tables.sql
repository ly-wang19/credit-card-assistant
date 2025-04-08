CREATE TABLE IF NOT EXISTS credit_cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '信用卡名称',
    bank VARCHAR(50) NOT NULL COMMENT '发卡银行',
    annual_fee TEXT COMMENT '年费',
    points_rule TEXT COMMENT '积分规则',
    benefits TEXT COMMENT '权益',
    card_type VARCHAR(50) COMMENT '卡片类型',
    credit_level VARCHAR(50) COMMENT '信用等级',
    foreign_transaction_fee TEXT COMMENT '境外交易手续费',
    card_organization VARCHAR(50) COMMENT '发卡组织',
    application_condition TEXT COMMENT '申请条件',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 