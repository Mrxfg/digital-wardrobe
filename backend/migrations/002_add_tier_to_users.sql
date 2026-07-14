-- Migration: Add tier column to users table
-- This column tracks the user's subscription tier: "free" or "premium"
-- Application default is "free", existing users get "free" by default

ALTER TABLE users
ADD COLUMN tier VARCHAR NOT NULL DEFAULT 'free';
