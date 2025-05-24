import asyncpg
import bcrypt


class DBControl:
    def __init__(self, dbs):
        self.dsn = f"postgresql://{dbs.IVS_SYSTEM_DB_USER}:{dbs.IVS_SYSTEM_DB_PASS}@localhost:{dbs.IVS_SYSTEM_DB_PORT}/{dbs.IVS_SYSTEM_DB_NAME}"
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        print("✅ Business Database connected")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("🛑 Business Database disconnected")

    async def _log_action(self, table, performed_by, entity_id, action, details=None):
        query = f"""
            INSERT INTO {table}_logs (performed_by, {table[:-1]}_id, action, details)
            VALUES ($1, $2, $3, $4)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, performed_by, entity_id, action, details or {})

    # -------- USERS --------
    async def insert_user(self, performed_by, name, email, password, role='editor'):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        query = """
            INSERT INTO users (name, email, password, role)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            user_id = await conn.fetchval(query, name, email, hashed, role)
            await self._log_action("users", performed_by, user_id, "create", {"name": name})
            return user_id

    async def update_user(self, performed_by, user_id, name=None, email=None, password=None, role=None):
        updates = []
        values = []
        if name:
            updates.append("name = ${}".format(len(values)+1))
            values.append(name)
        if email:
            updates.append("email = ${}".format(len(values)+1))
            values.append(email)
        if password:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            updates.append("password = ${}".format(len(values)+1))
            values.append(hashed)
        if role:
            updates.append("role = ${}".format(len(values)+1))
            values.append(role)
        values.append(user_id)
        query = f"""
            UPDATE users SET {', '.join(updates)} WHERE id = ${len(values)}
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, *values)
            await self._log_action("users", performed_by, user_id, "update")

    async def delete_user(self, performed_by, user_id):
        query = "DELETE FROM users WHERE id = $1"
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id)
            await self._log_action("users", performed_by, user_id, "delete")

    async def select_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, user_id)

    async def select_user_by_email(self, email):
        query = "SELECT * FROM users WHERE email = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, email)
        
    async def login_user(self, email: str, password: str):
        query = """
            SELECT id, name, email, password, role FROM users
            WHERE email = $1
        """
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(query, email)
            
            if not user:
                raise ValueError("Invalid email or password")
                
            if not bcrypt.checkpw(password.encode(), user['password'].encode()):
                raise ValueError("Invalid email or password")
                
            # Return user info without the password
            return {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }

    # -------- CHANNELS --------
    async def insert_channel(self, performed_by, name, config, plotting_config=None, status='active'):
        query = """
            INSERT INTO channels (name, status, confidence, overlapping, realtime,
                augmentation, tracking, reid, plotting_config)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            channel_id = await conn.fetchval(query,
                name, status,
                config['confidence'], config['overlapping'], config['realtime'],
                config['augmentation'], config['tracking'], config['reid'],
                plotting_config or {}
            )
            await self._log_action("channels", performed_by, channel_id, "create", {"name": name})
            return channel_id

    async def update_channel(self, performed_by, channel_id, name=None, status=None):
        updates = []
        values = []
        if name:
            updates.append("name = ${}".format(len(values)+1))
            values.append(name)
        if status:
            updates.append("status = ${}".format(len(values)+1))
            values.append(status)
        values.append(channel_id)
        query = f"UPDATE channels SET {', '.join(updates)} WHERE id = ${len(values)}"
        async with self.pool.acquire() as conn:
            await conn.execute(query, *values)
            await self._log_action("channels", performed_by, channel_id, "update")

    async def update_channel_processing_config(self, performed_by: int, channel_id: int, 
                                               confidence: float, overlapping: float, 
                                               realtime: bool, augmentation: bool, 
                                               tracking: bool, reid: bool):
        query = """
            UPDATE channels SET confidence = $1, overlapping = $2, realtime = $3, augmentation = $4, tracking = $5, reid = $6
            WHERE id = $7
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, confidence, overlapping, realtime, augmentation, tracking, reid, channel_id)
            await self._log_action("channels", performed_by, channel_id, "update", {"confidence": confidence, 
                                                                                    "overlapping": overlapping,
                                                                                    "realtime": realtime,
                                                                                    "augmentation": augmentation,
                                                                                    "tracking": tracking,
                                                                                    "reid": reid
                                                                                    })

    async def update_channel_plotting_config(self, performed_by, channel_id, plotting_config):
        query = "UPDATE channels SET plotting_config = $1 WHERE id = $2"
        async with self.pool.acquire() as conn:
            await conn.execute(query, plotting_config, channel_id)
            await self._log_action("channels", performed_by, channel_id, "update", {"plotting_config": plotting_config})

    async def delete_channel(self, performed_by, channel_id):
        query = "DELETE FROM channels WHERE id = $1"
        async with self.pool.acquire() as conn:
            await conn.execute(query, channel_id)
            await self._log_action("channels", performed_by, channel_id, "delete")

    async def select_channel_by_id(self, channel_id):
        query = "SELECT * FROM channels WHERE id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, channel_id)

    async def select_channel_by_name(self, name):
        query = "SELECT * FROM channels WHERE name = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, name)

    # -------- SOURCES --------
    async def insert_source(self, performed_by, channel_id, name, url, status='active'):
        query = """
            INSERT INTO sources (channel_id, name, url, status)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            source_id = await conn.fetchval(query, channel_id, name, url, status)
            await self._log_action("sources", performed_by, source_id, "create", {"name": name})
            return source_id

    async def update_source(self, performed_by, source_id, name=None, url=None, status=None):
        updates = []
        values = []
        if name:
            updates.append("name = ${}".format(len(values)+1))
            values.append(name)
        if url:
            updates.append("url = ${}".format(len(values)+1))
            values.append(url)
        if status:
            updates.append("status = ${}".format(len(values)+1))
            values.append(status)
        values.append(source_id)
        query = f"UPDATE sources SET {', '.join(updates)} WHERE id = ${len(values)}"
        async with self.pool.acquire() as conn:
            await conn.execute(query, *values)
            await self._log_action("sources", performed_by, source_id, "update")

    async def delete_source(self, performed_by, source_id):
        query = "DELETE FROM sources WHERE id = $1"
        async with self.pool.acquire() as conn:
            await conn.execute(query, source_id)
            await self._log_action("sources", performed_by, source_id, "delete")

    async def select_source_by_id(self, source_id):
        query = "SELECT * FROM sources WHERE id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, source_id)

    async def select_source_by_channel_id_source_name(self, channel_id, source_name):
        query = "SELECT * FROM sources WHERE channel_id = $1 AND name = $2"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, channel_id, source_name)

    async def select_source_by_channel_name_source_name(self, channel_name, source_name):
        query = """
            SELECT s.* FROM sources s
            JOIN channels c ON s.channel_id = c.id
            WHERE c.name = $1 AND s.name = $2
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, channel_name, source_name)

    # -------- MODELS --------
    async def insert_model(self, name, task, weight, classes):
        query = """
            INSERT INTO models (name, task, weight, classes)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, name, task, weight, classes)

    async def update_model(self, model_id, name=None, task=None, weight=None, classes=None):
        updates = []
        values = []
        if name:
            updates.append("name = ${}".format(len(values)+1))
            values.append(name)
        if task:
            updates.append("task = ${}".format(len(values)+1))
            values.append(task)
        if weight:
            updates.append("weight = ${}".format(len(values)+1))
            values.append(weight)
        if classes is not None:
            updates.append("classes = ${}".format(len(values)+1))
            values.append(classes)
        values.append(model_id)
        query = f"UPDATE models SET {', '.join(updates)} WHERE id = ${len(values)}"
        async with self.pool.acquire() as conn:
            await conn.execute(query, *values)

    async def delete_model(self, model_id):
        query = "DELETE FROM models WHERE id = $1"
        async with self.pool.acquire() as conn:
            await conn.execute(query, model_id)

    async def select_model_by_id(self, model_id):
        query = "SELECT * FROM models WHERE id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, model_id)

    async def select_model_by_name(self, name):
        query = "SELECT * FROM models WHERE name = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, name)

    # -------- M2M RELATIONS --------
    async def add_user_to_channel(self, channel_id, user_id):
        query = """
            INSERT INTO channels_users (channel_id, user_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, channel_id, user_id)

    async def add_model_to_channel(self, channel_id, model_id):
        query = """
            INSERT INTO channels_models (channel_id, model_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, channel_id, model_id)
