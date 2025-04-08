-- 创建信用卡信息表
CREATE TABLE IF NOT EXISTS credit_cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL COMMENT '银行名称',
    card_name VARCHAR(200) NOT NULL COMMENT '信用卡名称',
    card_level VARCHAR(500) COMMENT '卡片等级',
    annual_fee VARCHAR(200) COMMENT '年费政策',
    credit_limit VARCHAR(100) COMMENT '额度范围',
    points_rule TEXT COMMENT '积分规则',
    benefits TEXT COMMENT '权益信息',
    requirements TEXT COMMENT '申请条件',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_card (bank_name, card_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='信用卡信息表'; 