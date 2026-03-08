INSERT INTO users (email, hashed_password, is_active, is_superuser, created_at) 
VALUES ('larsenevans@proton.me', '$2b$12$8wQaq8OqcjKLZhn95MTm/Otok78yDFo16MsT3wKVkh.u9cSgVuOwS', true, true, now()) 
ON CONFLICT (email) DO NOTHING;
