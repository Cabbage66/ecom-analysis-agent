SET NAMES utf8mb4;

SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '账号',
    `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码',
    `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '名称',
    `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色：user-普通用户，admin-管理员',
    `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '邮箱',
    `phone` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '手机号',
    `avatar` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '头像',
    `status` int NOT NULL COMMENT '状态：0-禁用，1-正常',
    `create_time` datetime NOT NULL COMMENT '创建时间',
    `update_time` datetime NOT NULL COMMENT '更新时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `username` (`username` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户信息表' ROW_FORMAT = Dynamic;

-- table of products
CREATE TABLE `products` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` varchar(100) NOT NULL COMMENT '商品名称',
    `category` varchar(50) NOT NULL COMMENT '类目',
    `description` text NOT NULL COMMENT '商品描述',
    `price` decimal(10, 2) NOT NULL COMMENT '售价',
    `stock` int NOT NULL DEFAULT '0' COMMENT '库存数量',
    `shelf_status` varchar(20) NOT NULL DEFAULT 'on_sale' COMMENT '上下架状态',
    `review_status` varchar(20) NOT NULL DEFAULT 'normal' COMMENT '人工复核状态',
    `create_time` datetime NOT NULL COMMENT '创建时间',
    `update_time` datetime NOT NULL COMMENT '更新时间',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '商品表';

-- table of orders
CREATE TABLE `orders` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `order_no` varchar(32) NOT NULL COMMENT '订单号',
    `product_id` int NOT NULL COMMENT '商品ID',
    `buyer_name` varchar(50) NOT NULL COMMENT '买家昵称',
    `quantity` int NOT NULL DEFAULT '1' COMMENT '购买数量',
    `amount` decimal(10, 2) NOT NULL COMMENT '实付金额',
    `status` varchar(20) NOT NULL DEFAULT 'completed' COMMENT '订单状态',
    `create_time` datetime NOT NULL COMMENT '创建时间',
    `update_time` datetime NOT NULL COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_no` (`order_no`),
    KEY `idx_orders_product_id` (`product_id`),
    CONSTRAINT `fk_orders_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '订单表';

--table of reviews
CREATE TABLE `reviews` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `product_id` int NOT NULL COMMENT '商品ID',
    `order_id` int DEFAULT NULL COMMENT '关联订单ID',
    `rating` int NOT NULL COMMENT '评分1-5',
    `content` text NOT NULL COMMENT '评价正文',
    `img` varchar(255) DEFAULT NULL COMMENT '评价图片相对路径',
    `create_time` datetime NOT NULL COMMENT '创建时间',
    `update_time` datetime NOT NULL COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_reviews_product_id` (`product_id`),
    KEY `idx_reviews_order_id` (`order_id`),
    CONSTRAINT `fk_reviews_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
    CONSTRAINT `fk_reviews_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '评价表';

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO
    `users`
VALUES (
        1,
        'admin',
        '$2b$12$ypJClLKejFCsyn2eltOco.YAmXory0HFjh7E/oHu9MBzDZZ6wYSSi',
        '管理员',
        'admin',
        'admin@system.cn',
        '13988776699',
        '/uploads/1790046856623_dc4830aa.jpg',
        1,
        '2026-09-11 15:30:07',
        '2026-09-22 11:14:34'
    );

INSERT INTO
    `users`
VALUES (
        2,
        'aaa',
        '$2a$10$phJ2k4sP5.c7T/LuXwzyTu/AlbbOFXblsAZEW6mIfh3koVxQ3Hhny',
        '小白',
        'user',
        'xiaobai@qq.com',
        '13899776688',
        '/uploads/1790046891012_452a9884.png',
        1,
        '2026-09-09 16:56:41',
        '2026-09-22 11:14:52'
    );

INSERT INTO
    `users`
VALUES (
        3,
        'bbb',
        '$2a$10$blJ4Qgbaqxm5jmUAWvuiRuKy/FiqbmFv.n1i0noM3pxUZrYhd2HNK',
        '小黑',
        'user',
        'xiaohei@163.com',
        '13799886699',
        '/uploads/1790046917012_b9ee534a.png',
        1,
        '2026-09-22 11:15:00',
        '2026-09-22 11:15:30'
    );

SET FOREIGN_KEY_CHECKS = 1;