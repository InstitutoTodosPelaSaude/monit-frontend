// Executado pelo entrypoint oficial via mongosh
(() => {
  const dbName = process.env.MONGO_APP_DB;
  const user   = process.env.MONGO_APP_USER;
  const pass   = process.env.MONGO_APP_PASS;

  if (!dbName || !user || !pass) {
    print("[init] MONGO_APP_DB/MONGO_APP_USER/MONGO_APP_PASS ausentes — pulando criação do usuário de app.");
    return;
  }

  const appdb = db.getSiblingDB(dbName);
  const existing = appdb.getUser(user);

  if (existing) {
    print(`[init] Usuário de app '${user}' já existe no DB '${dbName}'.`);
  } else {
    appdb.createUser({
      user: user,
      pwd:  pass,
      roles: [{ role: "readWrite", db: dbName }]
    });
    print(`[init] Usuário de app '${user}' criado no DB '${dbName}'.`);
  }
})();
