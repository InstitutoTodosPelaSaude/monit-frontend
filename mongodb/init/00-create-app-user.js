// Executed by the official entrypoint via mongosh
(() => {
  const dbName = process.env.MONGO_APP_DB;
  const user   = process.env.MONGO_APP_USER;
  const pass   = process.env.MONGO_APP_PASS;

  if (!dbName || !user || !pass) {
    print("[init] MONGO_APP_DB/MONGO_APP_USER/MONGO_APP_PASS missing — skipping app user creation.");
    return;
  }

  const appdb = db.getSiblingDB(dbName);
  const existing = appdb.getUser(user);

  if (existing) {
    print(`[init] App user '${user}' already exists in DB '${dbName}'.`);
  } else {
    appdb.createUser({
      user: user,
      pwd:  pass,
      roles: [{ role: "readWrite", db: dbName }]
    });
    print(`[init] App user '${user}' created in DB '${dbName}'.`);
  }
})();
