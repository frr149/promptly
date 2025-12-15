# TypeScript Domain Model Architecture Blueprint

---

## 🤖 FOR AI CODE ASSISTANTS

When generating TypeScript code for this project, you MUST follow these mandatory rules:

### MANDATORY RULES (MUST)

1. **Hybrid Type Strategy:**
   - USE branded types for simple validated primitives (Currency, EmailAddress, UserId)
   - USE discriminated unions with `kind` field for complex domain entities (Money, Order, User)

2. **Factory Pattern (REQUIRED):**
   - ALL domain objects MUST be created through factory functions
   - NEVER use object literals to create domain objects
   - ALL factories MUST validate inputs using type guards before creating objects
   - ALWAYS throw descriptive errors for invalid inputs

3. **Runtime Validation (REQUIRED):**
   - EVERY factory function MUST validate ALL inputs
   - USE type guards (`is*`) for validation
   - NEVER skip validation - no exceptions

4. **Immutability (REQUIRED):**
   - ALL domain types MUST be readonly
   - USE `readonly` modifiers on all properties
   - USE `ReadonlyArray<T>` for arrays
   - NEVER mutate existing objects - always return new instances

5. **Equality Operations (REQUIRED):**
   - EVERY domain type MUST implement an `isEqual` function
   - Branded types: use reference equality on underlying primitives
   - Discriminated unions: use structural equality (compare all properties)
   - Collections: use multiset equality (counting approach)

6. **Type Guards (REQUIRED):**
   - EVERY domain type MUST have a corresponding guard function
   - Guards MUST use type predicates: `(x: unknown): x is Type`
   - Guards MUST validate the `kind` discriminator first (for discriminated unions)
   - Guards MUST validate ALL required properties

7. **Error Handling (REQUIRED):**
   - ALL domain errors MUST extend `AppError` base class
   - ALWAYS include `userInfo` metadata with context
   - USE error chaining via `previous` parameter when appropriate

8. **Testing (REQUIRED):**
   - EVERY feature MUST have both unit tests AND property-based tests
   - Unit tests: test specific scenarios, error conditions, immutability
   - Property-based tests: test algebraic properties and equivalence relations
   - ALWAYS test: reflexivity, symmetry, transitivity for equality operations

9. **File Organization (REQUIRED):**
   - `*.types.ts` - Type definitions only (no runtime code)
   - `*.make.ts` - Factory functions with validation
   - `*.guard.ts` - Type guards
   - `*.ops.ts` - Operations (pure functions)
   - `*.errors.ts` - Error class definitions

10. **Numeric Precision:**
    - USE `bigint` for money and precise integer calculations
    - NEVER use `number` for financial calculations
    - Literal syntax: `42n` (with `n` suffix)

### FORBIDDEN PATTERNS (NEVER)

❌ **NEVER** create domain objects with object literals - ALWAYS use factories
❌ **NEVER** skip runtime validation in factory functions
❌ **NEVER** mutate domain objects - always create new instances
❌ **NEVER** use `number` for money calculations - use `bigint`
❌ **NEVER** forget to implement `isEqual` for domain types
❌ **NEVER** skip the `kind` discriminator in discriminated unions
❌ **NEVER** forget defensive copying in factory functions
❌ **NEVER** compare objects with `===` - use `isEqual` for value equality
❌ **NEVER** skip type guard validation before operations
❌ **NEVER** write only unit tests - include property-based tests too
❌ **NEVER** add references to yourself (Claude, Claude Code, AI assistants, etc.) in code, comments, documentation, or commit messages

### CODE GENERATION CHECKLIST

Before completing code generation, verify:

- [ ] Factory function validates ALL inputs with type guards?
- [ ] All type properties marked as `readonly`?
- [ ] Discriminated union has `kind` field?
- [ ] **For discriminated unions: Asked user about flyweight pattern?**
- [ ] Type guard validates all required properties?
- [ ] `isEqual` function implemented for the type?
- [ ] Factory makes defensive copies of mutable inputs?
- [ ] Factory uses `Object.freeze()` where appropriate?
- [ ] Error classes extend `AppError` with `userInfo`?
- [ ] Both unit tests AND property-based tests written?
- [ ] Equivalence relations tested (reflexivity, symmetry, transitivity)?
- [ ] Immutability tested (original objects not mutated)?
- [ ] File naming follows conventions (*.types.ts, *.make.ts, etc.)?
- [ ] **Code, comments, and commit messages free of AI/Claude self-references?**

### OUTPUT STYLE

All generated code, comments, documentation, and commit messages MUST appear as if written by a human developer. NEVER include:

- References to AI assistants (Claude, Claude Code, GPT, etc.)
- Co-authorship attributions to AI
- Mentions of automated generation
- Links to AI tools or services

Write commit messages in first person as the developer making the change.

### PATTERN TEMPLATES

**Branded Type Pattern:**
```typescript
// 1. Define symbol and type
const SYMBOL: unique symbol = Symbol("TypeName");
export type TypeName<Param> = Param & { readonly [SYMBOL]: true };

// 2. Factory with validation
export function makeTypeName<Param>(value: Param): TypeName<Param> {
    if (!isValid(value)) throw new InvalidError(value);
    return value as TypeName<Param>;
}

// 3. Guard
export function isTypeName(x: unknown): x is TypeName<Param> {
    return typeof x === "string" && isValid(x);
}
```

**Discriminated Union Pattern:**
```typescript
// 1. Define type with kind
export type Entity = {
    readonly kind: "Entity",
    readonly field1: Type1,
    readonly field2: Type2
};

// 2. Factory with full validation
export function makeEntity(field1: Type1, field2: Type2): Entity {
    if (!isType1(field1)) throw new InvalidError(field1);
    if (!isType2(field2)) throw new InvalidError(field2);
    return { kind: "Entity", field1, field2 };
}

// 3. Guard validating all fields
export function isEntity(x: unknown): x is Entity {
    return typeof x === "object" && x !== null
        && (x as any).kind === "Entity"
        && isType1((x as any).field1)
        && isType2((x as any).field2);
}

// 4. Equality operation
export function isEqual(left: unknown, right: unknown): boolean {
    if (left === right) return true;
    if (!isEntity(left) || !isEntity(right)) return false;
    return isEqual(left.field1, right.field1)
        && isEqual(left.field2, right.field2);
}
```

### ⚠️ IMPORTANT: Ask About Flyweight Pattern for Discriminated Unions

**When creating a NEW discriminated union domain object, you MUST:**

1. **First, explain JavaScript equality to the user:**
   ```
   JavaScript equality reminder:
   - Reference equality (===): compares if two variables point to the same object in memory
   - Structural equality: compares if two objects have the same property values

   For discriminated unions (objects):
   - WITHOUT flyweight: each factory call creates a NEW object
     const a = makeEntity(...); const b = makeEntity(...);
     a === b // false (different objects, even with same values)
     Need structural comparison: isEqual(a, b)

   - WITH flyweight: factory returns cached instances for same identity
     const a = makeEntity("id1", ...); const b = makeEntity("id1", ...);
     a === b // true (same cached object)
     Reference equality works: a === b
   ```

2. **Analyze if flyweight makes sense for THIS specific domain object:**
   - Does it have a natural identity/key that makes instances interchangeable?
   - Will there be many instances with duplicate identities?
   - Is it conceptually a "value object" that can be shared?

3. **Present pros and cons for THIS specific case:**
   ```
   For [DomainObjectName], flyweight pattern would:

   ✅ BENEFITS:
   - Memory efficiency: Only one instance per unique identity (estimate: X instances)
   - Fast equality: Reference equality (===) instead of structural comparison
   - Cache-friendly: Better CPU cache locality
   - Guaranteed immutability: Cached instances can be frozen

   ❌ DRAWBACKS:
   - Global state: Factory maintains a persistent cache
   - Testing complexity: May need to clear cache between tests
   - Memory leaks: If identities are dynamically generated, cache grows unbounded
   - Added complexity: Factory logic becomes more complex
   - Thread safety: Requires synchronization in multi-threaded contexts

   ASSESSMENT for [DomainObjectName]:
   - Expected instances: [estimate based on domain]
   - Identity cardinality: [fixed set like currencies, or unbounded like user IDs?]
   - Memory impact: [calculate: instances × ~48 bytes per object]
   - Equality frequency: [how often will equality comparisons happen?]
   ```

4. **Ask the user:**
   ```
   Should I implement the flyweight pattern for [DomainObjectName]?

   Options:
   A) YES - Implement flyweight (cached instances, === equality)
   B) NO - Standard factory (new instances, structural equality via isEqual)

   Recommendation: [Your analysis-based recommendation]
   ```

5. **Implement based on user choice:**
   - If YES: Add cache Map in factory, implement instance caching
   - If NO: Standard factory without caching

**Flyweight Implementation Pattern (if user chooses YES):**
```typescript
// Cache for flyweight instances
const entityCache = new Map<IdentityKey, Entity>();

export function makeEntity(id: EntityId, field: Type): Entity {
    // 1. Validate inputs
    if (!isEntityId(id)) throw new InvalidError(id);
    if (!isType(field)) throw new InvalidError(field);

    // 2. Create identity key for cache lookup
    const cacheKey = id; // or composite key: `${id}|${field}` if multiple fields define identity

    // 3. Return cached instance if exists
    if (entityCache.has(cacheKey)) {
        return entityCache.get(cacheKey)!;
    }

    // 4. Create new instance
    const instance: Entity = Object.freeze({
        kind: "Entity",
        id,
        field
    });

    // 5. Cache and return
    entityCache.set(cacheKey, instance);
    return instance;
}

// Optional: Cache management utilities
export function clearEntityCache(): void {
    entityCache.clear();
}

export function getEntityCacheSize(): number {
    return entityCache.size;
}
```

**Note:** Branded types (simple primitives) get flyweight behavior for FREE via JavaScript string interning. Only ask about flyweight for discriminated unions (objects).

---

See detailed patterns and examples below for complete guidance.

---

## Overview

This document defines architectural patterns and coding guidelines for building **type-safe domain models** in TypeScript. These patterns emphasize **compile-time type safety**, **runtime validation**, **precise arithmetic**, and **immutability** throughout.

Use this blueprint when building domain-driven applications that require:

- Strong type safety with branded/nominal types
- Immutable data structures
- Precise numeric operations (e.g., financial calculations)
- Clear separation between domain logic and data transfer
- Comprehensive test coverage with both unit and property-based tests

---

## 🗂️ Directory Structure

Every project following this blueprint MUST use the following structure:

```text
project-root/
├── src/
│   ├── core/                    # Foundational utilities (shared across domains)
│   │   ├── errors.base.ts       # AppError base class
│   │   └── guards.base.ts       # Common type guards (isFiniteNumber, etc.)
│   │
│   ├── <domain>/                # Domain modules (one directory per domain concept)
│   │   ├── <domain>.types.ts    # Type definitions (branded types, discriminated unions)
│   │   ├── <domain>.make.ts     # Factory functions with runtime validation
│   │   ├── <domain>.guard.ts    # Type guards (runtime type predicates)
│   │   ├── <domain>.ops.ts      # Operations (pure functions on domain types)
│   │   ├── <domain>.errors.ts   # Domain-specific error classes
│   │   ├── <domain>.dto.types.ts # DTO type definitions (optional - for persistence)
│   │   └── <domain>.dto.ops.ts   # Domain ↔ DTO conversions (optional)
│   │
│   └── index.ts                 # Main entry point (optional barrel exports)
│
├── test/
│   ├── unit/                    # Example-based tests
│   │   └── <domain>.<feature>.unit.test.ts
│   │
│   └── pbt/                     # Property-based tests (fast-check)
│       └── <domain>.<feature>.pbt.test.ts
│
├── package.json
├── tsconfig.json                # TypeScript configuration
├── tsconfig.test.json           # Test-specific TypeScript config (optional)
└── vitest.config.ts             # Vitest configuration
```

---

## 📝 Naming Conventions

### File Naming Rules

Files MUST follow a strict **dot-separated pattern** indicating their purpose:

| Pattern | Purpose | Examples |
|---------|---------|----------|
| `*.types.ts` | Type definitions only (no runtime code) | `user.types.ts`, `order.types.ts` |
| `*.make.ts` | Factory functions (constructors with validation) | `user.make.ts`, `order.make.ts` |
| `*.guard.ts` | Type guards (runtime validation predicates) | `user.guard.ts`, `order.guard.ts` |
| `*.ops.ts` | Operations (pure functions on types) | `user.ops.ts`, `order.ops.ts` |
| `*.errors.ts` | Error class definitions | `user.errors.ts`, `order.errors.ts` |
| `*.dto.types.ts` | Data Transfer Object types | `user.dto.types.ts` |
| `*.dto.ops.ts` | DTO conversion operations | `user.dto.ops.ts` |
| `*.base.ts` | Base/foundational utilities | `errors.base.ts`, `guards.base.ts` |

### Test File Naming Rules

| Pattern | Purpose | Examples |
|---------|---------|----------|
| `*.unit.test.ts` | Example-based unit tests | `order.calculate.unit.test.ts` |
| `*.pbt.test.ts` | Property-based tests | `order.calculate.pbt.test.ts` |

### Function Naming Rules

| Pattern | Purpose | Examples |
|---------|---------|----------|
| `make*` | Factory functions (MUST validate inputs) | `makeUser`, `makeOrder`, `makeId` |
| `is*` | Type guards (MUST return type predicates) | `isUser`, `isOrder`, `isValidEmail` |
| `*ToDTO` | Domain → DTO conversion | `userToDTO`, `orderToDTO` |
| `*FromDTO` | DTO → Domain conversion | `userFromDTO`, `orderFromDTO` |
| Operation names | Domain operations | `add`, `multiply`, `compare`, `merge` |

### Type Naming Rules

| Pattern | Purpose | Examples |
|---------|---------|----------|
| PascalCase | Domain types | `User`, `Order`, `EmailAddress`, `OrderId` |
| `*DTO` suffix | Data Transfer Objects | `UserDTO`, `OrderDTO` |
| `*Error` suffix | Error classes | `InvalidEmailError`, `OrderNotFoundError` |

---

## 🏗️ Core Architectural Patterns

### 1. Branded Types with Phantom Types

**Rule:** Use branded types to create **nominal types** from structural types for simple validated primitives.

**When to use:** See "Choosing Between Branded Types and Discriminated Unions" below for detailed guidance.

**Primary use cases:**

- Simple validated primitives (Currency codes, Email addresses, User IDs)
- Types that need generic parameterization (e.g., `Currency<Code>`)
- Performance-critical primitives with high volume
- Thin wrappers around primitive values with no additional properties

**Pattern:**

```typescript
// Define an unexported unique symbol for the brand
const EMAIL_SYMBOL: unique symbol = Symbol("Email");

// Create branded type using intersection
export type EmailAddress = string & {
  readonly [EMAIL_SYMBOL]: true
};
```

**Factory with Runtime Validation (REQUIRED):**

```typescript
export function makeEmail(raw: string): EmailAddress {
    // 1. Normalize input
    const normalized = raw.trim().toLowerCase();

    // 2. Validate at runtime (REQUIRED - never skip validation)
    if (!isValidEmailFormat(normalized)) {
        throw new InvalidEmailError(raw, { reason: 'invalid format' });
    }

    // 3. Cast to branded type ONLY after validation
    return normalized as EmailAddress;
}
```

**Benefits:**

- Prevents accidental mixing of similar types (compile-time safety)
- Forces validation through factory functions
- No runtime overhead (erased at runtime)
- Can still use as underlying type when needed with explicit casting

---

### 2. Discriminated Unions with `kind` Field

**Rule:** Complex domain entities MUST use a **`kind` discriminator** for runtime type narrowing.

**When to use:** See "Choosing Between Branded Types and Discriminated Unions" below for detailed guidance.

**Primary use cases:**

- Domain entities with multiple properties (Money, Order, User)
- Types with multiple variants/states needing exhaustive pattern matching
- Rich objects requiring runtime introspection and debugging visibility

**Pattern:**

```typescript
// Each variant MUST have a unique literal `kind` value
export type Order = {
    readonly kind: "Order",
    readonly id: OrderId,
    readonly items: ReadonlyArray<OrderItem>,
    readonly total: Money
};

export type Draft = {
    readonly kind: "Draft",
    readonly items: ReadonlyArray<OrderItem>
};

// Sum type (union) - can represent multiple states
export type OrderState = Order | Draft;
```

**Usage in Type Guards:**

```typescript
export function isOrder(x: unknown): x is Order {
    return typeof x === "object" && x !== null
        && (x as any).kind === "Order";  // Discriminator check
}

export function isDraft(x: unknown): x is Draft {
    return typeof x === "object" && x !== null
        && (x as any).kind === "Draft";
}
```

**Benefits:**

- Enables exhaustive pattern matching
- TypeScript can narrow types automatically
- Clear runtime type identification
- Makes illegal states unrepresentable

---

### Choosing Between Branded Types and Discriminated Unions

**Rule:** Use a **hybrid approach** - choose the pattern based on the complexity and characteristics of your domain type.

#### Use Branded Types For: Simple Validated Primitives

**When to use:**

- Type is conceptually a primitive value (string, number) with validation constraints
- No additional properties beyond the validated value
- Needs to be parameterized with type information (e.g., `Currency<Code>`)
- Performance-critical code with high volume of instances
- Wants to leverage TypeScript's structural typing for the underlying primitive

**Examples:**

- `Currency<Code extends IsoCode>` - just a validated ISO code string
- `EmailAddress` - just a validated email string
- `UserId` - just a validated user ID string
- `PositiveInteger` - just a number with constraints
- `NonEmptyString` - just a string with validation

**Key Characteristic:** These types are **thin wrappers around primitives** with no additional behavior or properties.

```typescript
// Branded type example
const CURRENCY_SYMBOL: unique symbol = Symbol("Currency");
export type Currency<Code extends IsoCode> = Code & {
  readonly [CURRENCY_SYMBOL]: true
};

// Can be parameterized - preserves Code at type level
export function makeMoney<Code extends IsoCode>(
    amount: bigint,
    currency: Currency<Code>
): Money<Code> { ... }
```

#### Use Discriminated Unions For: Domain Entities

**When to use:**

- Type represents a domain entity with multiple properties
- Has meaningful structure beyond a single value
- May have multiple variants/states
- Needs runtime introspection and debugging visibility
- Benefits from consistent pattern across all domain types

**Examples:**

- `Money` - has amount, currency, and kind
- `Order` - has id, items, total, status
- `User` - has id, name, email, role
- `Address` - has street, city, country
- `MoneyBag` - collection of money amounts

**Key Characteristic:** These types are **rich domain entities** with structure and behavior.

```typescript
// Discriminated union example
export type Money = {
    readonly kind: "Money",
    readonly minor: bigint,
    readonly currency: Currency<IsoCode>  // Uses branded type for the code
};

// Cannot be parameterized meaningfully
export function makeMoney(
    amount: bigint,
    currency: Currency<IsoCode>
): Money { ... }
```

#### Why Discriminated Unions Lose Generic Parameters

When converting from branded type to discriminated union, you lose the ability to parameterize with specific type information. Here's why:

**With Branded Types (Generic Parameter Preserved):**

```typescript
// Branded type - Code is preserved at TYPE level
type Currency<Code extends IsoCode> = Code & { readonly [BRAND]: true };

// Money can be parameterized with specific currency
type Money<Code extends IsoCode> = {
    readonly kind: "Money",
    readonly minor: bigint,
    readonly currency: Currency<Code>  // Type knows EXACTLY which code
};

// Factory preserves the Code type parameter
function makeMoney<Code extends IsoCode>(
    amount: bigint,
    currency: Currency<Code>
): Money<Code> {  // Returns Money<"USD"> if currency is Currency<"USD">
    return { kind: "Money", minor: amount, currency };
}

// Usage - TypeScript KNOWS this is specifically USD Money
const usdMoney: Money<"USD"> = makeMoney(100n, makeCurrency("USD"));
```

**With Discriminated Union (Generic Parameter Lost):**

```typescript
// Discriminated union - code is just a property VALUE
type Currency = {
    readonly kind: "Currency",
    readonly code: IsoCode  // Just a property - type is the UNION of all codes
};

// Money cannot be meaningfully parameterized
type Money = {
    readonly kind: "Money",
    readonly minor: bigint,
    readonly currency: Currency  // Type only knows it's SOME currency
};

// Could try to add generic parameter, but it provides NO VALUE:
type Money<Code extends IsoCode> = {
    readonly kind: "Money",
    readonly minor: bigint,
    readonly currency: Currency  // currency.code is IsoCode, not Code!
};
// The Code parameter has no connection to currency.code at runtime

// Factory cannot preserve specific code information
function makeMoney(amount: bigint, currency: Currency): Money {
    return { kind: "Money", minor: amount, currency };
}

// Usage - TypeScript only knows this is SOME Money, not specifically USD
const someMoney: Money = makeMoney(100n, makeCurrency("USD"));
// To check currency: someMoney.currency.code === "USD" (runtime check)
```

**The Core Issue:**

- Branded types are **type-level annotations** on primitive values → Code stays in the type system
- Discriminated unions are **runtime objects** with properties → code becomes a property value
- Generic parameters need compile-time type information, but `currency.code` is just a runtime value

**Trade-off:**

- Branded types: Better type-level precision, worse runtime visibility
- Discriminated unions: Better runtime visibility, lost type-level precision

**Recommended Pattern:**

For this architecture, use **branded types for primitives** (like Currency) and **discriminated unions for entities** (like Money). This gives you:

- Type-level precision where it matters (`Money<"USD">` vs `Money<"EUR">`)
- Runtime visibility for complex entities
- Performance benefits of primitives where appropriate
- Consistent pattern for entities

---

### 3. Factory Pattern (REQUIRED)

**Rule:** All domain objects MUST be created through factory functions, NEVER through direct object literals.

**Rule:** All factories MUST perform runtime validation before creating objects.

**Basic Factory:**

```typescript
export function makeOrder(
    id: OrderId,
    items: ReadonlyArray<OrderItem>
): Order {
    // 1. VALIDATE ALL INPUTS (REQUIRED)
    if (!isOrderId(id)) {
        throw new InvalidOrderError(id, { field: 'id', expectedType: 'OrderId' });
    }
    if (!Array.isArray(items) || items.length === 0) {
        throw new InvalidOrderError(items, { field: 'items', reason: 'must be non-empty array' });
    }
    if (!items.every(isOrderItem)) {
        throw new InvalidOrderError(items, { field: 'items', reason: 'contains invalid items' });
    }

    // 2. Calculate derived values
    const total = calculateTotal(items);

    // 3. Return immutable object
    return {
        kind: "Order",
        id,
        items: Object.freeze([...items]), // Defensive copy + freeze
        total
    };
}
```

**Convenience Factories:**

```typescript
// Provide domain-specific shortcuts
export const emptyOrder = (id: OrderId) => makeOrder(id, []);
export const singleItemOrder = (id: OrderId, item: OrderItem) => makeOrder(id, [item]);
```

**Identity/Special Value Factories:**

```typescript
// For mathematical operations
export const zero = <T extends Unit>(unit: T) => makeQuantity(0, unit);
export const one = <T extends Unit>(unit: T) => makeQuantity(1, unit);
```

**Factory with Dependency Injection (Advanced):**

```typescript
// Type for the created function
export type Repository<T> = {
    find: (id: string) => Promise<T | undefined>;
    save: (entity: T) => Promise<void>;
};

// Factory creates repository with injected storage
export function makeRepository<T>(storage: Storage): Repository<T> {
    return {
        async find(id: string): Promise<T | undefined> {
            return await storage.get(id);
        },
        async save(entity: T): Promise<void> {
            await storage.set(entity.id, entity);
        }
    };
}
```

---

### 4. Guard Functions (Type Predicates)

**Rule:** Every domain type MUST have a corresponding guard function for runtime validation.

**Pattern:**

```typescript
export function isOrder(x: unknown): x is Order {
    // 1. Check object structure
    if (typeof x !== "object" || x === null) return false;

    const obj = x as any;

    // 2. Check discriminator (if using discriminated unions)
    if (obj.kind !== "Order") return false;

    // 3. Validate all required fields
    if (!isOrderId(obj.id)) return false;
    if (!Array.isArray(obj.items)) return false;
    if (!obj.items.every(isOrderItem)) return false;
    if (!isMoney(obj.total)) return false;

    return true;
}
```

**Guard for Primitive Types:**

```typescript
export function isFiniteNumber(x: unknown): x is number {
    return typeof x === "number" && Number.isFinite(x);
}

export function isPositiveInteger(x: unknown): x is number {
    return typeof x === "number" && Number.isInteger(x) && x > 0;
}
```

**Composing Guards:**

```typescript
export function isNonEmptyArray<T>(
    x: unknown,
    itemGuard: (item: unknown) => item is T
): x is T[] {
    return Array.isArray(x) && x.length > 0 && x.every(itemGuard);
}
```

---

### 5. DTO Pattern

**Rule:** Separate domain objects (optimized for business logic) from DTOs (optimized for serialization/persistence).

**When to use:**

- Persisting to databases
- Sending over network/APIs
- Types contain bigint, Date, or other non-JSON types
- Need different structure for external vs internal representation

**Domain Type:**

```typescript
export type Money = {
    readonly kind: "Money",
    readonly amount: bigint,           // Runtime type: bigint (not JSON-serializable)
    readonly currency: CurrencyCode
};
```

**DTO Type:**

```typescript
export type MoneyDTO = {
    kind: "Money",
    amount: string,                     // Serialized bigint
    currency: string                    // Plain string, not branded
};
```

**Conversion Functions:**

```typescript
// Domain → DTO (for persistence/API responses)
export function moneyToDTO(m: Money): MoneyDTO {
    return {
        kind: "Money",
        amount: m.amount.toString(),
        currency: m.currency,
    };
}

// DTO → Domain (from persistence/API requests) - MUST validate
export function moneyFromDTO(dto: MoneyDTO): Money {
    if (dto.kind !== "Money") {
        throw new InvalidMoneyError(dto, { reason: 'wrong kind' });
    }

    const amount = BigInt(dto.amount);  // May throw if invalid
    const currency = makeCurrencyCode(dto.currency);  // Validates

    return { kind: "Money", amount, currency };
}
```

---

### 6. Error Handling

**Rule:** All domain errors MUST extend a base `AppError` class with structured metadata.

**Base Error Class:**

```typescript
export type UserInfo = Record<string, unknown>;

export class AppError extends Error {
    constructor(
        message: string,
        public readonly userInfo?: UserInfo,
        previous?: Error    // Error chaining
    ) {
        super(message, { cause: previous });
        this.name = new.target.name;
    }

    toJSON() {
        return {
            name: this.name,
            message: this.message,
            userInfo: this.userInfo ?? null,
            cause: this.cause instanceof Error
                ? { name: this.cause.name, message: this.cause.message }
                : undefined,
            stack: process.env.NODE_ENV === 'production' ? undefined : this.stack,
        };
    }
}
```

**Domain-Specific Errors:**

```typescript
export class InvalidOrderError extends AppError {
    constructor(wrongValue: unknown, userInfo?: UserInfo, previous?: Error) {
        const msg = typeof wrongValue === "object" ? "[InvalidOrder]" : String(wrongValue);
        super(msg, { wrongValue, ...userInfo }, previous);
    }
}

export class OrderNotFoundError extends AppError {
    constructor(orderId: string, userInfo?: UserInfo, previous?: Error) {
        super(`Order not found: ${orderId}`, { orderId, ...userInfo }, previous);
    }
}
```

**Error Throwing in Factories:**

```typescript
export function makeOrder(id: OrderId, items: ReadonlyArray<OrderItem>): Order {
    if (!isOrderId(id)) {
        // Include context in userInfo
        throw new InvalidOrderError(id, {
            field: 'id',
            expectedType: 'OrderId',
            receivedType: typeof id
        });
    }

    // Chain errors when catching and re-throwing
    try {
        const total = calculateTotal(items);
        return { kind: "Order", id, items, total };
    } catch (err) {
        throw new InvalidOrderError(items, { reason: 'calculation failed' }, err as Error);
    }
}
```

---

### 7. Polymorphic Operations

**Rule:** Use function overloads for type-safe polymorphic operations.

**Pattern:**

```typescript
// Overload 1: Strong type when types match at compile-time
export function combine<T extends Entity>(left: T, right: T): T;

// Overload 2: Runtime-friendly combinations
export function combine(left: Entity, right: unknown): Entity;
export function combine(left: unknown, right: Entity): Entity;

// Overload 3: Generic fallback
export function combine(left: unknown, right: unknown): Entity;

// Single implementation
export function combine(left: unknown, right: unknown): Entity {
    // Runtime dispatch based on type guards
    if (isOrder(left) && isOrder(right)) {
        return combineOrders(left, right);
    }
    if (isDraft(left) && isDraft(right)) {
        return combineDrafts(left, right);
    }
    throw new UnsupportedOperationError(left, right, { op: "combine" });
}
```

**Polymorphic Dispatch:**

```typescript
export function process(state: OrderState): ProcessedState {
    // TypeScript narrows types based on discriminator
    if (isOrder(state)) {
        return processOrder(state);
    }
    if (isDraft(state)) {
        return processDraft(state);
    }

    // Exhaustiveness check - TypeScript will error if new variants added
    const exhaustive: never = state;
    throw new Error(`Unhandled state: ${exhaustive}`);
}
```

---

### 8. Equality Operations

**Rule:** Every domain type MUST implement an `isEqual` operation for value-based comparison.

**Why:** JavaScript's `===` only checks reference equality for objects. Domain objects need value-based equality to properly compare instances.

#### Equality for Branded Types (Primitives)

Branded types wrap primitives, so use **reference equality** for the underlying value:

```typescript
// Currency is a branded string
export function isEqual(left: unknown, right: unknown): boolean {
    // 1. Fast path: same reference
    if (left === right) return true;

    // 2. Validate both are the correct type
    if (!isCurrency(left) || !isCurrency(right)) return false;

    // 3. Compare underlying primitive values (works because branded types are erased at runtime)
    return left === right;
}
```

**Key Points:**

- Branded types are erased at runtime → they're just primitives
- Reference equality `===` works for strings, numbers
- Fast and efficient

#### Equality for Discriminated Unions (Objects)

Domain entities need **structural equality** - compare all significant properties:

```typescript
// Money is a discriminated union with properties
export function isEqual(left: unknown, right: unknown): boolean {
    // 1. Fast path: same reference
    if (left === right) return true;

    // 2. Validate both are Money
    if (!isMoney(left) || !isMoney(right)) return false;

    // 3. Compare all significant properties
    return left.minor === right.minor
        && left.currency === right.currency;
    // Note: Don't compare 'kind' - already validated by type guard
}
```

**Key Points:**

- Two different objects with same values should be equal
- Compare all properties that define identity
- Use `===` for primitives, call `isEqual` for nested objects
- Skip comparing `kind` discriminator (already checked by guard)

#### Equality for Collections/Bags

Collections need **set-like equality** - same elements in any order:

```typescript
export function isEqualBag(left: MoneyBag, right: MoneyBag): boolean {
    // 1. Fast check: different sizes → not equal
    if (left.amounts.length !== right.amounts.length) return false;

    // 2. Count occurrences of each element in left
    const counts = new Map<string, number>();
    for (const money of left.amounts) {
        // Create unique key for this money instance
        const key = `${money.currency}|${money.minor.toString()}`;
        counts.set(key, (counts.get(key) ?? 0) + 1);
    }

    // 3. Decrement counts for elements in right
    for (const money of right.amounts) {
        const key = `${money.currency}|${money.minor.toString()}`;
        const current = counts.get(key);

        // Not found → bags are different
        if (current === undefined) return false;

        // Decrement or remove
        if (current === 1) {
            counts.delete(key);
        } else {
            counts.set(key, current - 1);
        }
    }

    // 4. All counts should be zero (map should be empty)
    return counts.size === 0;
}
```

**Key Points:**

- Use counting approach for multiset equality
- Create serializable keys for elements
- Handle duplicates correctly
- Order doesn't matter

#### Polymorphic Equality with Overloads

Use function overloads for type-safe polymorphic equality:

```typescript
// Overload 1: Strong type guarantee when both are same type
export function isEqual<T extends Entity>(left: T, right: T): boolean;

// Overload 2: Runtime-friendly combinations
export function isEqual(left: Entity, right: unknown): boolean;
export function isEqual(left: unknown, right: Entity): boolean;

// Overload 3: Generic fallback
export function isEqual(left: unknown, right: unknown): boolean;

// Single implementation with runtime dispatch
export function isEqual(left: unknown, right: unknown): boolean {
    // Use type guards to dispatch to specific implementations
    if (isMoney(left) && isMoney(right)) {
        return isEqualMoney(left, right);
    }

    if (isMoneyBag(left) && isMoneyBag(right)) {
        return isEqualBag(left, right);
    }

    // Different types → not equal
    return false;
}
```

#### Common Patterns

**1. Reference Equality Fast Path:**

Always start with reference check - two references to same object are always equal:

```typescript
if (left === right) return true;  // Same object or same primitive value
```

**2. Type Validation:**

Validate both operands before comparing properties:

```typescript
if (!isOrder(left) || !isOrder(right)) return false;
```

**3. Property Comparison:**

For objects, compare all identity-defining properties:

```typescript
return left.id === right.id           // Primitive comparison
    && isEqual(left.user, right.user)  // Nested object comparison
    && arraysEqual(left.items, right.items);  // Array comparison
```

**4. Nested Equality:**

For nested objects, recursively call their equality functions:

```typescript
export function isEqual(left: Order, right: Order): boolean {
    return left.id === right.id
        && isEqual(left.customer, right.customer)  // Uses Customer's isEqual
        && left.items.every((item, i) => isEqual(item, right.items[i]));
}
```

#### Testing Equivalence Relations

Every `isEqual` implementation MUST satisfy these mathematical properties:

**Property-Based Tests:**

```typescript
import fc from "fast-check";

// Reflexivity: x = x
test("isEqual is reflexive", () =>
    fc.assert(fc.property(arbitraryMoney, (x) => {
        expect(isEqual(x, x)).toBe(true);
    }))
);

// Symmetry: x = y ⟺ y = x
test("isEqual is symmetric", () =>
    fc.assert(fc.property(arbitraryMoney, arbitraryMoney, (x, y) => {
        expect(isEqual(x, y)).toBe(isEqual(y, x));
    }))
);

// Transitivity: x = y ∧ y = z ⟹ x = z
test("isEqual is transitive", () =>
    fc.assert(fc.property(arbitraryMoney, arbitraryMoney, arbitraryMoney, (x, y, z) => {
        if (isEqual(x, y) && isEqual(y, z)) {
            expect(isEqual(x, z)).toBe(true);
        }
    }))
);
```

**Unit Tests:**

```typescript
test("equal values from different factories are equal", () => {
    const a = makeMoney(100n, makeCurrency("USD"));
    const b = makeMoney(100n, makeCurrency("USD"));

    // Different objects, same values
    expect(a).not.toBe(b);  // Reference inequality
    expect(isEqual(a, b)).toBe(true);  // Value equality
});

test("different values are not equal", () => {
    const a = makeMoney(100n, makeCurrency("USD"));
    const b = makeMoney(200n, makeCurrency("USD"));

    expect(isEqual(a, b)).toBe(false);
});
```

---

### 9. Immutability Patterns

**Rule:** All data structures MUST be readonly and immutable.

**Readonly Types:**

```typescript
export type Order = Readonly<{
    kind: "Order",
    id: OrderId,
    items: ReadonlyArray<OrderItem>,
    total: Money
}>;

// Or use readonly modifiers
export type Order = {
    readonly kind: "Order",
    readonly id: OrderId,
    readonly items: ReadonlyArray<OrderItem>,
    readonly total: Money
};
```

**Defensive Copying in Factories:**

```typescript
export function makeOrder(
    id: OrderId,
    items: ReadonlyArray<OrderItem>
): Order {
    // Defensive copy to avoid sharing mutable references
    const itemsCopy: OrderItem[] = items.slice();

    return {
        kind: "Order",
        id,
        items: Object.freeze(itemsCopy),  // Runtime immutability
        total: calculateTotal(itemsCopy)
    };
}
```

**Update Operations Return New Instances:**

```typescript
export function addItem(order: Order, item: OrderItem): Order {
    // Never mutate - create new instance via factory
    return makeOrder(order.id, [...order.items, item]);
}
```

---

## 🧪 Testing Strategy

### Two-Tier Testing Approach (REQUIRED)

Every domain feature MUST have both:

1. **Unit Tests** (`test/unit/`): Example-based tests for specific scenarios
2. **Property-Based Tests** (`test/pbt/`): Generative testing for invariants using `fast-check`

### Unit Test Structure

```typescript
import { describe, test, expect } from "vitest";
import { makeOrder, makeOrderItem } from "../../src/order/order.make.js";

describe("Order.addItem (unit)", () => {
    test("adds item and recalculates total", () => {
        const order = makeOrder(makeOrderId("1"), []);
        const item = makeOrderItem("Widget", 100n);

        const updated = addItem(order, item);

        expect(updated.items).toHaveLength(1);
        expect(updated.total.amount).toBe(100n);
    });

    test("immutability: original order unchanged", () => {
        const order = makeOrder(makeOrderId("1"), []);
        const item = makeOrderItem("Widget", 100n);
        const before = { ...order };

        const updated = addItem(order, item);

        expect(order).toEqual(before);
        expect(updated).not.toBe(order);
    });

    test("throws on invalid item", () => {
        const order = makeOrder(makeOrderId("1"), []);

        expect(() => addItem(order, null as any)).toThrow(InvalidOrderItemError);
    });
});
```

### Property-Based Test Structure

Test **algebraic properties** and **domain invariants**:

```typescript
import fc from "fast-check";
import { test, expect } from "vitest";

// Define arbitraries for your domain
const arbitraryAmount = fc.bigInt({ min: 0n, max: 1_000_000n });
const arbitraryItem = fc.record({
    name: fc.string({ minLength: 1 }),
    price: arbitraryAmount,
});

// Test algebraic properties
test("addItem is associative", () =>
    fc.assert(
        fc.property(arbitraryItem, arbitraryItem, arbitraryItem, (a, b, c) => {
            const order = emptyOrder(makeOrderId("1"));
            const left = addItem(addItem(addItem(order, a), b), c);
            const right = addItem(addItem(addItem(order, a), b), c);
            expect(left).toEqual(right);
        })
    )
);

// Test domain invariants
test("order total always equals sum of item prices", () =>
    fc.assert(
        fc.property(fc.array(arbitraryItem, { minLength: 1 }), (items) => {
            const order = makeOrder(makeOrderId("1"), items);
            const expectedTotal = items.reduce((sum, item) => sum + item.price, 0n);
            expect(order.total.amount).toBe(expectedTotal);
        })
    )
);
```

### Properties to Test (Checklist)

**Equivalence Relations (for `isEqual` operations):**

- [ ] Reflexivity: `isEqual(a, a) === true`
- [ ] Symmetry: `isEqual(a, b) === isEqual(b, a)`
- [ ] Transitivity: if `a=b` and `b=c` then `a=c`

**Algebraic Properties (for operations):**

- [ ] Commutativity: `op(a, b) === op(b, a)` (if applicable)
- [ ] Associativity: `op(op(a, b), c) === op(a, op(b, c))` (if applicable)
- [ ] Identity: `op(x, identity) === x` (if applicable)

**Domain Invariants (ALWAYS test):**

- [ ] Closure: factory output satisfies guard predicates
- [ ] Immutability: objects don't mutate after creation
- [ ] Type safety: all properties maintain valid types
- [ ] Determinism: same inputs → same outputs
- [ ] Guard/Factory consistency: `is*(make*(...)) === true`

---

## ⚙️ TypeScript & Build Configuration

### tsconfig.json (REQUIRED settings)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "rootDir": "src",
    "outDir": "dist",
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true
  },
  "include": ["src"],
  "exclude": ["dist", "node_modules"]
}
```

### package.json (recommended scripts)

```json
{
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/index.ts",
    "typecheck": "tsc --noEmit",
    "typecheck:watch": "tsc --noEmit --watch",
    "test": "pnpm typecheck && vitest",
    "test:unit": "pnpm typecheck && vitest run test/unit",
    "test:pbt": "pnpm typecheck && vitest run test/pbt",
    "test:run": "pnpm typecheck && vitest run",
    "test:coverage": "pnpm typecheck && vitest run --coverage"
  }
}
```

### vitest.config.ts (recommended configuration)

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
    coverage: {
      provider: "v8",
      all: true,
      include: ["src/**/*.ts"],
      exclude: [
        "src/**/*.types.ts",   // Pure types: no runtime code
        "src/**/index.ts",     // Barrel files
        "test/**",
      ],
    },
  },
});
```

---

## 📋 Important Conventions

### ES Modules (REQUIRED)

- Project MUST use `"type": "module"` in package.json
- All imports MUST include `.js` extensions even for `.ts` files
- Example: `import { User } from "./user.types.js";`

### Numeric Precision (for financial/precise calculations)

- Use `bigint` for precise integer arithmetic (money, quantities)
- Never use `number` or floating point for financial calculations
- Literal syntax: `42n` (note the `n` suffix)
- WARNING: `1 !== 1n` in JavaScript

### Immutability (REQUIRED)

- All domain objects MUST be `readonly`
- Use `ReadonlyArray<T>` for arrays
- Use `Readonly<{...}>` for object types
- Make defensive copies in factory functions
- Operations MUST return new instances, never mutate

### Normalization (RECOMMENDED)

- Normalize input data before validation
- Common normalizations: trim, lowercase, uppercase
- Apply consistently across all factories

### Type Checking in Tests

- All test commands SHOULD run typecheck before executing
- Use `pnpm test:only` to skip typechecking (faster iteration during development)

---

## 🆕 Adding a New Domain Feature

When adding a new feature, follow this checklist:

### 1. Create Domain Files

```text
src/<domain>/
├── <domain>.types.ts      # Define types first
├── <domain>.make.ts       # Factory functions
├── <domain>.guard.ts      # Type guards
├── <domain>.ops.ts        # Operations
├── <domain>.errors.ts     # Custom errors
└── <domain>.dto.*.ts      # DTOs if needed for persistence
```

### 2. Define Types (`*.types.ts`)

- [ ] Use discriminated union with `kind` field
- [ ] Make all fields `readonly`
- [ ] Use branded types if nominal typing needed
- [ ] Define sum types if multiple variants exist

### 3. Create Factory (`*.make.ts`)

- [ ] VALIDATE all inputs using type guards
- [ ] Throw descriptive errors on invalid input
- [ ] Cast to branded type ONLY after validation
- [ ] Create convenience factories for common cases
- [ ] Make defensive copies of mutable inputs
- [ ] Use `Object.freeze()` for runtime immutability

### 4. Add Guards (`*.guard.ts`)

- [ ] Use type predicate return type (`x is Type`)
- [ ] Check `kind` discriminator first (if using discriminated unions)
- [ ] Validate ALL required fields
- [ ] Compose with existing guards
- [ ] Test with property-based tests that `is*(make*(...)) === true`

### 5. Implement Operations (`*.ops.ts`)

- [ ] Define type-safe overloads for polymorphic operations
- [ ] Implement polymorphic dispatch if needed
- [ ] Ensure immutability (NEVER mutate)
- [ ] Return new instances via factories
- [ ] Validate inputs using guards

### 6. Define Errors (`*.errors.ts`)

- [ ] Extend `AppError` base class
- [ ] Include meaningful `userInfo` metadata
- [ ] Support error chaining via `previous` parameter
- [ ] Provide helpful error messages

### 7. Write Tests

**Unit tests** (`test/unit/<domain>.<feature>.unit.test.ts`):

- [ ] Test happy paths with examples
- [ ] Test error conditions
- [ ] Test immutability
- [ ] Test edge cases

**Property-based tests** (`test/pbt/<domain>.<feature>.pbt.test.ts`):

- [ ] Test algebraic properties (if applicable)
- [ ] Test equivalence relations
- [ ] Test domain invariants
- [ ] Test determinism
- [ ] Test guard/factory consistency

### 8. Update Exports (if using barrel files)

- [ ] Export types from `*.types.ts`
- [ ] Export factories from `*.make.ts`
- [ ] Export guards from `*.guard.ts`
- [ ] Export operations from `*.ops.ts`

---

## 🎯 Summary of Key Principles

1. **Hybrid Type Strategy**: Use branded types for simple validated primitives (Currency, EmailAddress, UserId) and discriminated unions for complex domain entities (Money, Order, User)
2. **Runtime Validation**: All factories MUST validate inputs before creating objects
3. **Immutability Everywhere**: All data structures are readonly and never mutated
4. **Factory Pattern**: All objects created through validated factory functions
5. **Type Narrowing**: Use `kind` discriminator for entities, branded types preserve generic parameters for primitives
6. **Guard Functions**: Runtime validation with type predicates for every domain type
7. **Structured Errors**: Extend AppError with metadata
8. **Two-Tier Testing**: Unit tests + property-based tests for every feature
9. **File Organization**: Consistent naming (`*.types`, `*.make`, `*.guard`, `*.ops`, `*.errors`)
10. **ES Modules**: Use `.js` extensions in imports

---

## 📚 Reference Implementation

For a complete reference implementation, see the domains in this project:

- `src/currency/` - Simple branded type with validation
- `src/money/` - Complex type with discriminated unions and operations
- `src/fx/` - Advanced patterns with dependency injection

Each domain demonstrates all patterns described in this blueprint.

---

**Blueprint Version:** 2.1
**Last Updated:** 2025-01-13

**Changelog:**

- v2.1: Added flyweight pattern decision workflow for discriminated unions
- v2.1: LLM must explain JS equality, analyze trade-offs, and ask user before implementing discriminated unions
- v2.1: Added flyweight implementation pattern template with cache management
- v2.0: Added comprehensive AI/LLM assistant instructions section with mandatory rules, forbidden patterns, checklist, and pattern templates
- v1.1: Added hybrid approach guidance (branded types for primitives, discriminated unions for entities)
- v1.1: Added detailed explanation of why discriminated unions lose generic parameters
- v1.1: Added comprehensive equality operations guidance
- v1.0: Initial blueprint release
