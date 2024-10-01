-- Create the tavern schema
CREATE SCHEMA tavern;

-- Install the pgcrypto extension for password hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the users table
CREATE TABLE tavern.users (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL
);

-- Create the register_user function
CREATE FUNCTION tavern.register_user(username TEXT, password TEXT) RETURNS tavern.users AS $$
DECLARE
  new_user tavern.users;
BEGIN
  INSERT INTO tavern.users (username, password_hash)
  VALUES (username, crypt(password, gen_salt('bf')))
  RETURNING * INTO new_user;
  
  RETURN new_user;
END;
$$ LANGUAGE plpgsql STRICT SECURITY DEFINER;

-- Create the authenticate function
CREATE FUNCTION tavern.authenticate(username TEXT, password TEXT) RETURNS tavern.users AS $$
DECLARE
  user_record tavern.users;
BEGIN
  SELECT * INTO user_record
  FROM tavern.users
  WHERE users.username = authenticate.username;

  IF user_record.password_hash = crypt(password, user_record.password_hash) THEN
    RETURN user_record;
  ELSE
    RETURN NULL;
  END IF;
END;
$$ LANGUAGE plpgsql STRICT SECURITY DEFINER;

-- Grant usage on the tavern schema to public
GRANT USAGE ON SCHEMA tavern TO PUBLIC;

-- Grant execute permission on the functions to public
GRANT EXECUTE ON FUNCTION tavern.register_user(TEXT, TEXT) TO PUBLIC;
GRANT EXECUTE ON FUNCTION tavern.authenticate(TEXT, TEXT) TO PUBLIC;

-- Grant select permission on the users table to public
GRANT SELECT ON tavern.users TO PUBLIC;
