CREATE TABLE users(
  id SERIAL PRIMARY KEY,
  telegram_id BIGINT NOT NULL UNIQUE,
  username TEXT NULL,
);

CREATE TABLE resources(
  id SERIAL PRIMARY KEY,
  link TEXT NOT NULL
);

CREATE TABLE subscriptions(
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE
);

CREATE TABLE settings(
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  notifications_on BOOLEAN DEFAULT TRUE,
);