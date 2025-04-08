-- Set up JWT secrets and expiry
ALTER SYSTEM SET jwt_secret TO '${JWT_SECRET}';
ALTER SYSTEM SET jwt_exp TO ${JWT_EXPIRY};
ALTER DATABASE postgres SET "app.settings.jwt_secret" TO '${JWT_SECRET}';
ALTER DATABASE postgres SET "app.settings.jwt_exp" TO '${JWT_EXPIRY}'; 