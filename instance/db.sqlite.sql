BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "diet" (
	"id"	INTEGER,
	"name"	VARCHAR(150) NOT NULL,
	"code"	VARCHAR(50) NOT NULL,
	"is_basic"	BOOLEAN NOT NULL DEFAULT 0,
	"is_light"	BOOLEAN NOT NULL DEFAULT 0,
	"is_diabetes"	BOOLEAN NOT NULL DEFAULT 0,
	"is_milk_free"	BOOLEAN NOT NULL DEFAULT 0,
	"is_mix"	BOOLEAN NOT NULL DEFAULT 0,
	"is_peg"	BOOLEAN NOT NULL DEFAULT 0,
	"is_restrictive"	BOOLEAN NOT NULL DEFAULT 0,
	"active"	BOOLEAN NOT NULL DEFAULT 1,
	"notes"	TEXT,
	UNIQUE("code"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "resident" (
	"id"	INTEGER,
	"last_name"	TEXT NOT NULL,
	"first_name"	TEXT NOT NULL,
	"room_number"	TEXT,
	"floor"	INTEGER,
	"is_active"	BOOLEAN NOT NULL DEFAULT 1,
	"is_hospital"	BOOLEAN NOT NULL DEFAULT 0,
	"is_pass"	BOOLEAN NOT NULL DEFAULT 0,
	"has_diet"	BOOLEAN NOT NULL DEFAULT 0,
	"needs_attention"	BOOLEAN NOT NULL DEFAULT 1,
	"notes"	TEXT,
	"created_at"	DATETIME NOT NULL,
	"updated_at"	DATETIME NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	CONSTRAINT "uq_resident_identity" UNIQUE("last_name","first_name")
);
CREATE TABLE IF NOT EXISTS "resident_diet" (
	"id"	INTEGER,
	"resident_id"	INTEGER NOT NULL,
	"diet_id"	INTEGER NOT NULL,
	"breakfast"	BOOLEAN NOT NULL DEFAULT 0,
	"lunch"	BOOLEAN NOT NULL DEFAULT 0,
	"dinner"	BOOLEAN NOT NULL DEFAULT 0,
	"notes"	TEXT(1000),
	PRIMARY KEY("id"),
	FOREIGN KEY("diet_id") REFERENCES "diet_old"("id"),
	FOREIGN KEY("resident_id") REFERENCES "resident"("id")
);
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER NOT NULL,
	"username"	VARCHAR(50) NOT NULL,
	"password_hash"	VARCHAR(255) NOT NULL,
	"is_active"	BOOLEAN,
	"created_at"	DATETIME,
	PRIMARY KEY("id"),
	UNIQUE("username")
);
CREATE INDEX IF NOT EXISTS "idx_resident_dashboard" ON "resident" (
	"floor",
	"room_number",
	"needs_attention"
);
CREATE UNIQUE INDEX IF NOT EXISTS "uq_resident_one_diet" ON "resident_diet" (
	"resident_id"
);
COMMIT;
