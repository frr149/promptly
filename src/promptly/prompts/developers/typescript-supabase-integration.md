{% include 'developers/typescript.md' %}

---

{% include 'developers/supabase.md' %}

---

# INTEGRACIÓN TypeScript + Supabase

Las reglas anteriores de TypeScript y Supabase se aplican independientemente. Esta sección añade **ÚNICAMENTE** patrones de integración.

## Arquitectura de 3 Capas

```text
DOMAIN (TypeScript)
  ↓ *FromDTO() / *ToDTO()
DTO (Tipos generados)
  ↓ Supabase Client
BD (PostgreSQL/Supabase)
```

**Regla fundamental**: Nunca mezcles capas. La conversión es explícita.

## Patrones de Integración

### 1. IDs: UUID (BD) → Branded Type (TS)

```sql
CREATE TABLE orders (id UUID PRIMARY KEY DEFAULT uuid_generate_v4());
```

```typescript
const ORDER_ID: unique symbol = Symbol("OrderId");
export type OrderId = string & { readonly [ORDER_ID]: true };

export function makeOrderId(id: string): OrderId {
    if (!isValidUUID(id)) throw new InvalidOrderIdError(id);
    return id as OrderId;
}
```

### 2. Money: BIGINT (BD) → bigint (TS) → string (JSON)

```sql
CREATE TABLE orders (total_cents BIGINT NOT NULL CHECK (total_cents >= 0));
```

```typescript
export type Money = { readonly kind: "Money", readonly amount: bigint, readonly currency: Currency };

export function moneyFromDTO(cents: string): Money {
    return makeMoney(BigInt(cents), makeCurrency("USD"));
}

export function moneyToDTO(money: Money): string {
    return money.amount.toString();
}
```

### 3. Enums: CREATE TYPE (BD) → String Literal Union (TS)

```sql
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped');
CREATE TABLE orders (status order_status NOT NULL DEFAULT 'pending');
```

```typescript
export type OrderStatus = 'pending' | 'paid' | 'shipped';

export function isOrderStatus(x: unknown): x is OrderStatus {
    return typeof x === 'string' && ['pending', 'paid', 'shipped'].includes(x);
}

export function orderFromDTO(dto: OrderDTO): Order {
    if (!isOrderStatus(dto.status)) throw new InvalidOrderError(dto, { field: 'status' });
    return { ...makeOrder(...), status: dto.status };
}
```

### 4. Timestamps: TIMESTAMPTZ (BD) → Date (TS) → ISO string (JSON)

```sql
CREATE TABLE posts (
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```typescript
export type Post = { readonly kind: "Post", readonly createdAt: Date, readonly updatedAt: Date };

export function postFromDTO(dto: PostDTO): Post {
    return { kind: "Post", createdAt: new Date(dto.created_at), updatedAt: new Date(dto.updated_at) };
}

export function postToDTO(post: Post): PostInsertDTO {
    return { created_at: post.createdAt.toISOString(), updated_at: post.updatedAt.toISOString() };
}
```

### 5. Relaciones: Foreign Keys (BD) → Propiedades (TS)

```sql
CREATE TABLE posts (
    author_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE
);
CREATE INDEX idx_posts_author_id ON posts(author_id);
```

```typescript
// Relación lazy (solo ID)
export type Post = { readonly kind: "Post", readonly authorId: UserId };

// Relación eager (join)
export type PostWithAuthor = { readonly kind: "PostWithAuthor", readonly author: Profile };

// Query con join
const { data } = await supabase.from('posts').select('*, author:profiles!author_id(*)');
```

### 6. JSONB: Flexible (BD) → Validado (TS)

```sql
CREATE TABLE posts (metadata JSONB NOT NULL DEFAULT '{}'::jsonb);
CREATE INDEX idx_posts_metadata ON posts USING GIN (metadata);
```

```typescript
export type PostMetadata = { readonly version: number, readonly tags?: ReadonlyArray<string> };

export function postFromDTO(dto: PostDTO): Post {
    if (typeof dto.metadata.version !== 'number') throw new InvalidPostError(dto);
    return { kind: "Post", metadata: { version: dto.metadata.version, tags: dto.metadata.tags ? Object.freeze([...dto.metadata.tags]) : undefined } };
}
```

### 7. Doble Validación: Constraints (BD) + Factories (TS)

**Defense in Depth**: BD previene corrupción, TS previene errores lógicos

```sql
CREATE TABLE profiles (
    username TEXT CHECK (length(username) >= 3 AND username ~ '^[a-zA-Z0-9_]+$')
);
```

```typescript
export function makeProfile(username: string): Profile {
    const normalized = username.trim().toLowerCase();
    if (normalized.length < 3 || !/^[a-zA-Z0-9_]+$/.test(normalized)) {
        throw new InvalidUsernameError(username);
    }
    return { kind: "Profile", username: normalized };
}
```

### 8. RLS Policies (BD) + Autorización (TS)

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "posts_update_own" ON posts FOR UPDATE USING (auth.uid() = author_id);
```

```typescript
export function canEditPost(currentUser: UserId, post: Post): boolean {
    return currentUser === post.authorId;
}

export function updatePost(currentUser: UserId, post: Post, updates: Partial<Post>): Post {
    if (!canEditPost(currentUser, post)) throw new UnauthorizedError({ userId: currentUser, postId: post.id });
    return { ...post, ...updates }; // RLS en BD rechazará si lógica TS falla
}
```

### 9. Storage: Buckets (Supabase) + Metadatos (BD)

```sql
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES profiles(id),
    bucket_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    UNIQUE(bucket_id, file_path)
);
```

```typescript
export async function uploadFile(supabase: SupabaseClient, userId: UserId, file: File): Promise<FileUpload> {
    const fileId = makeFileId(crypto.randomUUID());
    const filePath = `${userId}/${fileId}`;

    // 1. Upload a Storage
    const { error: storageError } = await supabase.storage.from('avatars').upload(filePath, file);
    if (storageError) throw new FileUploadError(storageError);

    // 2. Metadatos en BD
    const { data, error: dbError } = await supabase.from('file_uploads').insert({ id: fileId, user_id: userId, bucket_id: 'avatars', file_path: filePath, file_size: file.size.toString() }).select().single();

    if (dbError) {
        await supabase.storage.from('avatars').remove([filePath]); // Rollback
        throw new FileUploadError(dbError);
    }

    return fileUploadFromDTO(data);
}
```

## Estructura de Proyecto

```text
project/
├── supabase/migrations/        # SQL versionado
├── src/
│   ├── types/database.types.ts # GENERADO: supabase gen types
│   ├── lib/supabase.ts
│   ├── <domain>/
│   │   ├── *.types.ts          # Domain types
│   │   ├── *.make.ts           # Factories
│   │   ├── *.guard.ts          # Type guards
│   │   ├── *.dto.ts            # DTO ↔ Domain
│   │   ├── *.repository.ts     # Supabase queries
│   │   └── *.service.ts        # Lógica de negocio
└── test/
    ├── unit/                   # Domain tests
    └── integration/            # Supabase tests
```

## Patrón Repository

Encapsula Supabase, convierte DTO ↔ Domain

```typescript
export class OrderRepository {
    constructor(private readonly supabase: SupabaseClient<Database>) {}

    async findById(id: OrderId): Promise<Order | null> {
        const { data, error } = await this.supabase.from('orders').select('*').eq('id', id).single();
        if (error?.code === 'PGRST116') return null;
        if (error) throw new RepositoryError(error);
        return orderFromDTO(data); // DTO → Domain
    }

    async save(order: Order): Promise<Order> {
        const dto = orderToDTO(order); // Domain → DTO
        const { data, error } = await this.supabase.from('orders').upsert(dto).select().single();
        if (error) throw new RepositoryError(error);
        return orderFromDTO(data);
    }
}
```

## Patrón Service

Orquesta lógica de negocio

```typescript
export class OrderService {
    constructor(private readonly orderRepo: OrderRepository, private readonly userRepo: UserRepository) {}

    async createOrder(userId: UserId, items: OrderItem[]): Promise<Order> {
        const user = await this.userRepo.findById(userId);
        if (!user) throw new UserNotFoundError({ userId });

        const order = makeOrder({ id: makeOrderId(crypto.randomUUID()), userId, items, status: 'pending', createdAt: new Date() });
        return await this.orderRepo.save(order);
    }
}
```

## Workflow

```bash
# 1. Diseñar migración
supabase migration new create_orders
# Editar supabase/migrations/XXXXXX_create_orders.sql

# 2. Aplicar y generar tipos
supabase db reset
supabase gen types typescript --local > src/types/database.types.ts

# 3-7. Crear types, DTOs, repository, service, tests
```

## Reglas de Integración

✅ **SIEMPRE**:

- Genera tipos DTO con `supabase gen types` tras cada migración
- Convierte DTO → Domain con validación en `*FromDTO()`
- Convierte Domain → DTO en `*ToDTO()` (sin validación, ya validado)
- Encapsula Supabase en repositories
- Valida en BD (constraints) Y en TS (factories)
- Implementa RLS en BD Y autorización en TS

❌ **NUNCA**:

- Uses `Database['public']['Tables']...` en lógica de dominio
- Omitas validación en `*FromDTO()`
- Escribas queries de Supabase fuera de repositories
- Mezcles lógica de negocio con acceso a datos
- Uses `number` para dinero (usa `bigint` en TS, `BIGINT` en SQL)
