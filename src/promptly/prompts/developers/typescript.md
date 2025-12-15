# TypeScript Domain Model Architecture Blueprint

---

## PARA ASISTENTES DE CÓDIGO IA

Cuando generes código TypeScript para este proyecto, DEBES seguir estas reglas obligatorias:

### REGLAS OBLIGATORIAS (MUST)

1. **Estrategia de Tipos Híbrida:**
   - USA branded types para primitivos validados simples (Currency, EmailAddress, UserId)
   - USA discriminated unions con campo `kind` para entidades de dominio complejas (Money, Order, User)

2. **Patrón Factory (OBLIGATORIO):**
   - TODOS los objetos de dominio DEBEN crearse mediante funciones factory
   - NUNCA uses object literals para crear objetos de dominio
   - TODAS las factories DEBEN validar inputs usando type guards antes de crear objetos
   - SIEMPRE lanza errores descriptivos para inputs inválidos

3. **Validación en Runtime (OBLIGATORIO):**
   - CADA función factory DEBE validar TODOS los inputs
   - USA type guards (`is*`) para validación
   - NUNCA omitas la validación - sin excepciones

4. **Inmutabilidad (OBLIGATORIO):**
   - TODOS los tipos de dominio DEBEN ser readonly
   - USA modificadores `readonly` en todas las propiedades
   - USA `ReadonlyArray<T>` para arrays
   - NUNCA mutes objetos existentes - siempre devuelve nuevas instancias

5. **Operaciones de Igualdad (OBLIGATORIO):**
   - CADA tipo de dominio DEBE implementar una función `isEqual`
   - Branded types: usa igualdad por referencia en primitivos subyacentes
   - Discriminated unions: usa igualdad estructural (compara todas las propiedades)
   - Colecciones: usa igualdad de multiset (enfoque de conteo)

6. **Type Guards (OBLIGATORIO):**
   - CADA tipo de dominio DEBE tener una función guard correspondiente
   - Los guards DEBEN usar type predicates: `(x: unknown): x is Type`
   - Los guards DEBEN validar el discriminador `kind` primero (para discriminated unions)
   - Los guards DEBEN validar TODAS las propiedades requeridas

7. **Gestión de Errores (OBLIGATORIO):**
   - TODOS los errores de dominio DEBEN extender la clase base `AppError`
   - SIEMPRE incluye metadatos `userInfo` con contexto
   - USA encadenamiento de errores mediante el parámetro `previous` cuando sea apropiado

8. **Testing (OBLIGATORIO):**
   - CADA funcionalidad DEBE tener tests unitarios Y tests basados en propiedades
   - Tests unitarios: prueban escenarios específicos, condiciones de error, inmutabilidad
   - Tests basados en propiedades: prueban propiedades algebraicas y relaciones de equivalencia
   - SIEMPRE prueba: reflexividad, simetría, transitividad para operaciones de igualdad

9. **Organización de Archivos (OBLIGATORIO):**
   - `*.types.ts` - Solo definiciones de tipos (sin código runtime)
   - `*.make.ts` - Funciones factory con validación
   - `*.guard.ts` - Type guards
   - `*.ops.ts` - Operaciones (funciones puras)
   - `*.errors.ts` - Definiciones de clases de error

10. **Precisión Numérica:**
    - USA `bigint` para dinero y cálculos enteros precisos
    - NUNCA uses `number` para cálculos financieros
    - Sintaxis literal: `42n` (con sufijo `n`)

### PATRONES PROHIBIDOS (NUNCA)

❌ **NUNCA** crees objetos de dominio con object literals - USA SIEMPRE factories
❌ **NUNCA** omitas la validación en runtime en funciones factory
❌ **NUNCA** mutes objetos de dominio - siempre crea nuevas instancias
❌ **NUNCA** uses `number` para cálculos de dinero - usa `bigint`
❌ **NUNCA** olvides implementar `isEqual` para tipos de dominio
❌ **NUNCA** omitas el discriminador `kind` en discriminated unions
❌ **NUNCA** olvides el copiado defensivo en funciones factory
❌ **NUNCA** compares objetos con `===` - usa `isEqual` para igualdad por valor
❌ **NUNCA** omitas la validación de type guard antes de operaciones
❌ **NUNCA** escribas solo tests unitarios - incluye también tests basados en propiedades
❌ **NUNCA** añadas referencias a ti mismo (Claude, Claude Code, asistentes IA, etc.) en código, comentarios, documentación o mensajes de commit

### CHECKLIST DE GENERACIÓN DE CÓDIGO

Antes de completar la generación de código, verifica:

- [ ] ¿La función factory valida TODOS los inputs con type guards?
- [ ] ¿Todas las propiedades de tipo marcadas como `readonly`?
- [ ] ¿La discriminated union tiene campo `kind`?
- [ ] Para discriminated unions: ¿Preguntaste al usuario sobre el patrón flyweight?
- [ ] ¿El type guard valida todas las propiedades requeridas?
- [ ] ¿La función `isEqual` está implementada para el tipo?
- [ ] ¿La factory hace copias defensivas de inputs mutables?
- [ ] ¿La factory usa `Object.freeze()` donde sea apropiado?
- [ ] ¿Las clases de error extienden `AppError` con `userInfo`?
- [ ] ¿Están escritos TANTO tests unitarios COMO tests basados en propiedades?
- [ ] ¿Relaciones de equivalencia probadas (reflexividad, simetría, transitividad)?
- [ ] ¿Inmutabilidad probada (objetos originales no mutados)?
- [ ] ¿Los nombres de archivo siguen las convenciones (*.types.ts, *.make.ts, etc.)?
- [ ] ¿Código, comentarios y mensajes de commit libres de auto-referencias a IA/Claude?

### ESTILO DE OUTPUT

Todo el código generado, comentarios, documentación y mensajes de commit DEBEN aparecer como si fueran escritos por un desarrollador humano. NUNCA incluyas:

- Referencias a asistentes IA (Claude, Claude Code, GPT, etc.)
- Atribuciones de coautoría a IA
- Menciones de generación automatizada
- Enlaces a herramientas o servicios de IA

Escribe mensajes de commit en primera persona como el desarrollador haciendo el cambio.

### PLANTILLAS DE PATRONES

**Patrón Branded Type:**

```typescript
// 1. Define símbolo y tipo
const SYMBOL: unique symbol = Symbol("TypeName");
export type TypeName<Param> = Param & { readonly [SYMBOL]: true };

// 2. Factory con validación
export function makeTypeName<Param>(value: Param): TypeName<Param> {
    if (!isValid(value)) throw new InvalidError(value);
    return value as TypeName<Param>;
}

// 3. Guard
export function isTypeName(x: unknown): x is TypeName<Param> {
    return typeof x === "string" && isValid(x);
}
```

**Patrón Discriminated Union:**

```typescript
// 1. Define tipo con kind
export type Entity = {
    readonly kind: "Entity",
    readonly field1: Type1,
    readonly field2: Type2
};

// 2. Factory con validación completa
export function makeEntity(field1: Type1, field2: Type2): Entity {
    if (!isType1(field1)) throw new InvalidError(field1);
    if (!isType2(field2)) throw new InvalidError(field2);
    return { kind: "Entity", field1, field2 };
}

// 3. Guard validando todos los campos
export function isEntity(x: unknown): x is Entity {
    return typeof x === "object" && x !== null
        && (x as any).kind === "Entity"
        && isType1((x as any).field1)
        && isType2((x as any).field2);
}

// 4. Operación de igualdad
export function isEqual(left: unknown, right: unknown): boolean {
    if (left === right) return true;
    if (!isEntity(left) || !isEntity(right)) return false;
    return isEqual(left.field1, right.field1)
        && isEqual(left.field2, right.field2);
}
```

### IMPORTANTE: Preguntar sobre el Patrón Flyweight para Discriminated Unions

**Cuando crees un NUEVO objeto de dominio con discriminated union, DEBES:**

1. **Primero, explicar la igualdad en JavaScript al usuario:**

   ```text
   Recordatorio de igualdad en JavaScript:
   - Igualdad por referencia (===): compara si dos variables apuntan al mismo objeto en memoria
   - Igualdad estructural: compara si dos objetos tienen los mismos valores de propiedades

   Para discriminated unions (objetos):
   - SIN flyweight: cada llamada a factory crea un objeto NUEVO
     const a = makeEntity(...); const b = makeEntity(...);
     a === b // false (objetos diferentes, incluso con los mismos valores)
     Necesita comparación estructural: isEqual(a, b)

   - CON flyweight: factory devuelve instancias cacheadas para la misma identidad
     const a = makeEntity("id1", ...); const b = makeEntity("id1", ...);
     a === b // true (mismo objeto cacheado)
     Funciona igualdad por referencia: a === b
   ```

2. **Analiza si flyweight tiene sentido para ESTE objeto de dominio específico:**
   - ¿Tiene una identidad/clave natural que hace las instancias intercambiables?
   - ¿Habrá muchas instancias con identidades duplicadas?
   - ¿Es conceptualmente un "value object" que puede compartirse?

3. **Presenta pros y contras para ESTE caso específico:**

   ```text
   Para [NombreDelObjetoDeDominio], el patrón flyweight resultaría en:

   ✅ BENEFICIOS:
   - Eficiencia de memoria: Solo una instancia por identidad única (estima: X instancias)
   - Igualdad rápida: Igualdad por referencia (===) en lugar de comparación estructural
   - Cache-friendly: Mejor localidad de caché de CPU
   - Inmutabilidad garantizada: Las instancias cacheadas pueden ser frozen

   ❌ DESVENTAJAS:
   - Estado global: Factory mantiene una caché persistente
   - Complejidad en testing: Puede necesitar limpiar caché entre tests
   - Memory leaks: Si las identidades se generan dinámicamente, la caché crece sin límite
   - Complejidad añadida: La lógica de factory se vuelve más compleja
   - Thread safety: Requiere sincronización en contextos multi-hilo

   EVALUACIÓN para [NombreDelObjetoDeDominio]:
   - Instancias esperadas: [estimación basada en dominio]
   - Cardinalidad de identidad: [conjunto fijo como monedas, o ilimitado como IDs de usuario?]
   - Impacto en memoria: [calcula: instancias × ~48 bytes por objeto]
   - Frecuencia de igualdad: [¿con qué frecuencia ocurrirán comparaciones de igualdad?]
   ```

4. **Pregunta al usuario:**

   ```text
   ¿Debería implementar el patrón flyweight para [NombreDelObjetoDeDominio]?

   Opciones:
   A) SÍ - Implementar flyweight (instancias cacheadas, igualdad ===)
   B) NO - Factory estándar (nuevas instancias, igualdad estructural vía isEqual)

   Recomendación: [Tu recomendación basada en análisis]
   ```

5. **Implementa según la elección del usuario:**
   - Si SÍ: Añade Map de caché en factory, implementa cacheo de instancias
   - Si NO: Factory estándar sin cacheo

**Patrón de Implementación Flyweight (si el usuario elige SÍ):**

```typescript
// Caché para instancias flyweight
const entityCache = new Map<IdentityKey, Entity>();

export function makeEntity(id: EntityId, field: Type): Entity {
    // 1. Validar inputs
    if (!isEntityId(id)) throw new InvalidError(id);
    if (!isType(field)) throw new InvalidError(field);

    // 2. Crear clave de identidad para búsqueda en caché
    const cacheKey = id; // o clave compuesta: `${id}|${field}` si múltiples campos definen identidad

    // 3. Devolver instancia cacheada si existe
    if (entityCache.has(cacheKey)) {
        return entityCache.get(cacheKey)!;
    }

    // 4. Crear nueva instancia
    const instance: Entity = Object.freeze({
        kind: "Entity",
        id,
        field
    });

    // 5. Cachear y devolver
    entityCache.set(cacheKey, instance);
    return instance;
}

// Opcional: Utilidades de gestión de caché
export function clearEntityCache(): void {
    entityCache.clear();
}

export function getEntityCacheSize(): number {
    return entityCache.size;
}
```

**Nota:** Los branded types (primitivos simples) obtienen comportamiento flyweight GRATIS mediante string interning de JavaScript. Solo pregunta sobre flyweight para discriminated unions (objetos).

---

Consulta los patrones y ejemplos detallados a continuación para una guía completa.

---

## Resumen

Patrones arquitectónicos para construir **modelos de dominio type-safe** en TypeScript con **seguridad de tipos en tiempo de compilación**, **validación en runtime**, **aritmética precisa** e **inmutabilidad**.

---

## Estructura de Directorios

Todo proyecto que siga este blueprint DEBE usar la siguiente estructura:

```text
project-root/
├── src/
│   ├── core/                    # Utilidades fundamentales (compartidas entre dominios)
│   │   ├── errors.base.ts       # Clase base AppError
│   │   └── guards.base.ts       # Type guards comunes (isFiniteNumber, etc.)
│   │
│   ├── <domain>/                # Módulos de dominio (un directorio por concepto de dominio)
│   │   ├── <domain>.types.ts    # Definiciones de tipos (branded types, discriminated unions)
│   │   ├── <domain>.make.ts     # Funciones factory con validación en runtime
│   │   ├── <domain>.guard.ts    # Type guards (predicados de tipo en runtime)
│   │   ├── <domain>.ops.ts      # Operaciones (funciones puras sobre tipos de dominio)
│   │   ├── <domain>.errors.ts   # Clases de error específicas del dominio
│   │   ├── <domain>.dto.types.ts # Definiciones de tipos DTO (opcional - para persistencia)
│   │   └── <domain>.dto.ops.ts   # Conversiones Domain ↔ DTO (opcional)
│   │
│   └── index.ts                 # Punto de entrada principal (barrel exports opcionales)
│
├── test/
│   ├── unit/                    # Tests basados en ejemplos
│   │   └── <domain>.<feature>.unit.test.ts
│   │
│   └── pbt/                     # Tests basados en propiedades (fast-check)
│       └── <domain>.<feature>.pbt.test.ts
│
├── package.json
├── tsconfig.json                # Configuración de TypeScript
├── tsconfig.test.json           # Configuración de TypeScript específica para tests (opcional)
└── vitest.config.ts             # Configuración de Vitest
```

---

## Convenciones de Nomenclatura

### Reglas de Nomenclatura de Archivos

Los archivos DEBEN seguir un **patrón estricto separado por puntos** indicando su propósito:

| Patrón | Propósito | Ejemplos |
|---------|---------|----------|
| `*.types.ts` | Solo definiciones de tipos (sin código runtime) | `user.types.ts`, `order.types.ts` |
| `*.make.ts` | Funciones factory (constructores con validación) | `user.make.ts`, `order.make.ts` |
| `*.guard.ts` | Type guards (predicados de validación en runtime) | `user.guard.ts`, `order.guard.ts` |
| `*.ops.ts` | Operaciones (funciones puras sobre tipos) | `user.ops.ts`, `order.ops.ts` |
| `*.errors.ts` | Definiciones de clases de error | `user.errors.ts`, `order.errors.ts` |
| `*.dto.types.ts` | Tipos Data Transfer Object | `user.dto.types.ts` |
| `*.dto.ops.ts` | Operaciones de conversión DTO | `user.dto.ops.ts` |
| `*.base.ts` | Utilidades base/fundamentales | `errors.base.ts`, `guards.base.ts` |

### Reglas de Nomenclatura de Archivos de Test

| Patrón | Propósito | Ejemplos |
|---------|---------|----------|
| `*.unit.test.ts` | Tests unitarios basados en ejemplos | `order.calculate.unit.test.ts` |
| `*.pbt.test.ts` | Tests basados en propiedades | `order.calculate.pbt.test.ts` |

### Reglas de Nomenclatura de Funciones

| Patrón | Propósito | Ejemplos |
|---------|---------|----------|
| `make*` | Funciones factory (DEBEN validar inputs) | `makeUser`, `makeOrder`, `makeId` |
| `is*` | Type guards (DEBEN devolver type predicates) | `isUser`, `isOrder`, `isValidEmail` |
| `*ToDTO` | Conversión Domain → DTO | `userToDTO`, `orderToDTO` |
| `*FromDTO` | Conversión DTO → Domain | `userFromDTO`, `orderFromDTO` |
| Nombres de operaciones | Operaciones de dominio | `add`, `multiply`, `compare`, `merge` |

### Reglas de Nomenclatura de Tipos

| Patrón | Propósito | Ejemplos |
|---------|---------|----------|
| PascalCase | Tipos de dominio | `User`, `Order`, `EmailAddress`, `OrderId` |
| Sufijo `*DTO` | Data Transfer Objects | `UserDTO`, `OrderDTO` |
| Sufijo `*Error` | Clases de error | `InvalidEmailError`, `OrderNotFoundError` |

---

## Patrones Arquitectónicos Core

### 1. Branded Types con Phantom Types

**Regla:** Usa branded types para crear **tipos nominales** a partir de tipos estructurales para primitivos validados simples.

**Cuándo usar:** Consulta "Elegir entre Branded Types y Discriminated Unions" más abajo para orientación detallada.

**Casos de uso principales:**

- Primitivos validados simples (códigos de moneda, direcciones de email, IDs de usuario)
- Tipos que necesitan parametrización genérica (ej: `Currency<Code>`)
- Primitivos críticos de rendimiento con alto volumen
- Wrappers delgados alrededor de valores primitivos sin propiedades adicionales

**Patrón:**

```typescript
// Define un símbolo único no exportado para la marca
const EMAIL_SYMBOL: unique symbol = Symbol("Email");

// Crea branded type usando intersección
export type EmailAddress = string & {
  readonly [EMAIL_SYMBOL]: true
};
```

**Factory con Validación en Runtime (OBLIGATORIO):**

```typescript
export function makeEmail(raw: string): EmailAddress {
    // 1. Normalizar input
    const normalized = raw.trim().toLowerCase();

    // 2. Validar en runtime (OBLIGATORIO - nunca omitir validación)
    if (!isValidEmailFormat(normalized)) {
        throw new InvalidEmailError(raw, { reason: 'invalid format' });
    }

    // 3. Castear a branded type SOLO después de validación
    return normalized as EmailAddress;
}
```

**Beneficios:**

- Previene mezcla accidental de tipos similares (seguridad en tiempo de compilación)
- Fuerza validación a través de funciones factory
- Sin overhead en runtime (borrado en runtime)
- Se puede usar como tipo subyacente cuando sea necesario con casting explícito

---

### 2. Discriminated Unions con Campo `kind`

**Regla:** Las entidades de dominio complejas DEBEN usar un **discriminador `kind`** para narrowing de tipos en runtime.

**Cuándo usar:** Consulta "Elegir entre Branded Types y Discriminated Unions" más abajo para orientación detallada.

**Casos de uso principales:**

- Entidades de dominio con múltiples propiedades (Money, Order, User)
- Tipos con múltiples variantes/estados que necesitan pattern matching exhaustivo
- Objetos ricos que requieren introspección en runtime y visibilidad de debugging

**Patrón:**

```typescript
// Cada variante DEBE tener un valor `kind` literal único
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

// Sum type (unión) - puede representar múltiples estados
export type OrderState = Order | Draft;
```

**Uso en Type Guards:**

```typescript
export function isOrder(x: unknown): x is Order {
    return typeof x === "object" && x !== null
        && (x as any).kind === "Order";  // Comprobación de discriminador
}

export function isDraft(x: unknown): x is Draft {
    return typeof x === "object" && x !== null
        && (x as any).kind === "Draft";
}
```

**Beneficios:**

- Habilita pattern matching exhaustivo
- TypeScript puede estrechar tipos automáticamente
- Identificación clara de tipos en runtime
- Hace estados ilegales irrepresentables

---

### Elegir entre Branded Types y Discriminated Unions

**Regla:** Usa un **enfoque híbrido**:

**Branded Types** → Primitivos validados simples (Currency, EmailAddress, UserId)

- Wrappers delgados alrededor de primitivos con validación
- Pueden ser parametrizados con información de tipo
- Instancias de alto volumen, críticas de rendimiento
- Ejemplo: `Currency<Code extends IsoCode>`

**Discriminated Unions** → Entidades de dominio con múltiples propiedades

- Objetos ricos con estructura y comportamiento
- Introspección en runtime y visibilidad de debugging
- Ejemplo: `Money`, `Order`, `User`

**Trade-off:** Los branded types preservan parámetros genéricos a nivel de tipo, las discriminated unions proporcionan visibilidad en runtime pero pierden precisión a nivel de tipo.

---

### 3. Patrón Factory (OBLIGATORIO)

**Regla:** Todos los objetos de dominio DEBEN crearse mediante funciones factory, NUNCA mediante object literals directos.

**Regla:** Todas las factories DEBEN realizar validación en runtime antes de crear objetos.

**Factory Básica:**

```typescript
export function makeOrder(
    id: OrderId,
    items: ReadonlyArray<OrderItem>
): Order {
    // 1. VALIDAR TODOS LOS INPUTS (OBLIGATORIO)
    if (!isOrderId(id)) {
        throw new InvalidOrderError(id, { field: 'id', expectedType: 'OrderId' });
    }
    if (!Array.isArray(items) || items.length === 0) {
        throw new InvalidOrderError(items, { field: 'items', reason: 'must be non-empty array' });
    }
    if (!items.every(isOrderItem)) {
        throw new InvalidOrderError(items, { field: 'items', reason: 'contains invalid items' });
    }

    // 2. Calcular valores derivados
    const total = calculateTotal(items);

    // 3. Devolver objeto inmutable
    return {
        kind: "Order",
        id,
        items: Object.freeze([...items]), // Copia defensiva + freeze
        total
    };
}
```

**Factories de Conveniencia:**

```typescript
export const emptyOrder = (id: OrderId) => makeOrder(id, []);
export const zero = <T extends Unit>(unit: T) => makeQuantity(0, unit);
```

---

### 4. Funciones Guard (Type Predicates)

**Regla:** Cada tipo de dominio DEBE tener una función guard correspondiente para validación en runtime.

**Patrón:**

```typescript
export function isOrder(x: unknown): x is Order {
    // 1. Comprobar estructura de objeto
    if (typeof x !== "object" || x === null) return false;

    const obj = x as any;

    // 2. Comprobar discriminador (si se usan discriminated unions)
    if (obj.kind !== "Order") return false;

    // 3. Validar todos los campos requeridos
    if (!isOrderId(obj.id)) return false;
    if (!Array.isArray(obj.items)) return false;
    if (!obj.items.every(isOrderItem)) return false;
    if (!isMoney(obj.total)) return false;

    return true;
}
```

**Guard para Tipos Primitivos:**

```typescript
export function isFiniteNumber(x: unknown): x is number {
    return typeof x === "number" && Number.isFinite(x);
}

export function isPositiveInteger(x: unknown): x is number {
    return typeof x === "number" && Number.isInteger(x) && x > 0;
}
```

**Componiendo Guards:**

```typescript
export function isNonEmptyArray<T>(
    x: unknown,
    itemGuard: (item: unknown) => item is T
): x is T[] {
    return Array.isArray(x) && x.length > 0 && x.every(itemGuard);
}
```

---

### 5. Patrón DTO

**Regla:** Separa objetos de dominio (optimizados para lógica de negocio) de DTOs (optimizados para serialización/persistencia).

**Cuándo usar:**

- Persistir en bases de datos
- Enviar por red/APIs
- Los tipos contienen bigint, Date, u otros tipos no-JSON
- Necesitas estructura diferente para representación externa vs interna

**Tipo de Dominio:**

```typescript
export type Money = {
    readonly kind: "Money",
    readonly amount: bigint,           // Tipo runtime: bigint (no serializable a JSON)
    readonly currency: CurrencyCode
};
```

**Tipo DTO:**

```typescript
export type MoneyDTO = {
    kind: "Money",
    amount: string,                     // bigint serializado
    currency: string                    // String plano, no branded
};
```

**Funciones de Conversión:**

```typescript
// Domain → DTO (para persistencia/respuestas API)
export function moneyToDTO(m: Money): MoneyDTO {
    return {
        kind: "Money",
        amount: m.amount.toString(),
        currency: m.currency,
    };
}

// DTO → Domain (desde persistencia/peticiones API) - DEBE validar
export function moneyFromDTO(dto: MoneyDTO): Money {
    if (dto.kind !== "Money") {
        throw new InvalidMoneyError(dto, { reason: 'wrong kind' });
    }

    const amount = BigInt(dto.amount);  // Puede lanzar si es inválido
    const currency = makeCurrencyCode(dto.currency);  // Valida

    return { kind: "Money", amount, currency };
}
```

---

### 6. Gestión de Errores

**Regla:** Todos los errores de dominio DEBEN extender una clase base `AppError` con metadatos estructurados.

**Clase Base de Error:**

```typescript
export type UserInfo = Record<string, unknown>;

export class AppError extends Error {
    constructor(
        message: string,
        public readonly userInfo?: UserInfo,
        previous?: Error    // Encadenamiento de errores
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

**Errores Específicos de Dominio:**

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

**Lanzamiento de Errores en Factories:**

```typescript
export function makeOrder(id: OrderId, items: ReadonlyArray<OrderItem>): Order {
    if (!isOrderId(id)) {
        // Incluir contexto en userInfo
        throw new InvalidOrderError(id, {
            field: 'id',
            expectedType: 'OrderId',
            receivedType: typeof id
        });
    }

    // Encadenar errores al capturar y relanzar
    try {
        const total = calculateTotal(items);
        return { kind: "Order", id, items, total };
    } catch (err) {
        throw new InvalidOrderError(items, { reason: 'calculation failed' }, err as Error);
    }
}
```

---

### 7. Operaciones Polimórficas

**Regla:** Usa function overloads para operaciones polimórficas type-safe.

**Patrón:**

```typescript
// Overload 1: Tipo fuerte cuando los tipos coinciden en tiempo de compilación
export function combine<T extends Entity>(left: T, right: T): T;

// Overload 2: Combinaciones amigables con runtime
export function combine(left: Entity, right: unknown): Entity;
export function combine(left: unknown, right: Entity): Entity;

// Overload 3: Fallback genérico
export function combine(left: unknown, right: unknown): Entity;

// Implementación única
export function combine(left: unknown, right: unknown): Entity {
    // Dispatch en runtime basado en type guards
    if (isOrder(left) && isOrder(right)) {
        return combineOrders(left, right);
    }
    if (isDraft(left) && isDraft(right)) {
        return combineDrafts(left, right);
    }
    throw new UnsupportedOperationError(left, right, { op: "combine" });
}
```

**Dispatch Polimórfico:**

```typescript
export function process(state: OrderState): ProcessedState {
    // TypeScript estrecha tipos basándose en el discriminador
    if (isOrder(state)) {
        return processOrder(state);
    }
    if (isDraft(state)) {
        return processDraft(state);
    }

    // Comprobación de exhaustividad - TypeScript dará error si se añaden nuevas variantes
    const exhaustive: never = state;
    throw new Error(`Unhandled state: ${exhaustive}`);
}
```

---

### 8. Operaciones de Igualdad

**Regla:** Cada tipo de dominio DEBE implementar una operación `isEqual` para comparación basada en valor.

**Por qué:** El `===` de JavaScript solo comprueba igualdad por referencia para objetos. Los objetos de dominio necesitan igualdad basada en valor para comparar instancias correctamente.

#### Patrones de Igualdad

**Branded Types (Primitivos):**

```typescript
export function isEqual(left: unknown, right: unknown): boolean {
    if (left === right) return true;
    if (!isCurrency(left) || !isCurrency(right)) return false;
    return left === right;  // Los primitivos usan igualdad por referencia
}
```

**Discriminated Unions (Objetos):**

```typescript
export function isEqual(left: unknown, right: unknown): boolean {
    if (left === right) return true;
    if (!isMoney(left) || !isMoney(right)) return false;
    return left.minor === right.minor && left.currency === right.currency;
}
```

**Colecciones (igualdad de multiset):**

```typescript
export function isEqualBag(left: MoneyBag, right: MoneyBag): boolean {
    if (left.amounts.length !== right.amounts.length) return false;
    const counts = new Map<string, number>();
    for (const money of left.amounts) {
        const key = `${money.currency}|${money.minor}`;
        counts.set(key, (counts.get(key) ?? 0) + 1);
    }
    for (const money of right.amounts) {
        const key = `${money.currency}|${money.minor}`;
        const current = counts.get(key);
        if (!current) return false;
        current === 1 ? counts.delete(key) : counts.set(key, current - 1);
    }
    return counts.size === 0;
}
```

#### Testear Relaciones de Equivalencia

Cada implementación de `isEqual` DEBE satisfacer estas propiedades matemáticas:

**Tests Basados en Propiedades:**

```typescript
import fc from "fast-check";

// Reflexividad: x = x
test("isEqual is reflexive", () =>
    fc.assert(fc.property(arbitraryMoney, (x) => {
        expect(isEqual(x, x)).toBe(true);
    }))
);

// Simetría: x = y ⟺ y = x
test("isEqual is symmetric", () =>
    fc.assert(fc.property(arbitraryMoney, arbitraryMoney, (x, y) => {
        expect(isEqual(x, y)).toBe(isEqual(y, x));
    }))
);

// Transitividad: x = y ∧ y = z ⟹ x = z
test("isEqual is transitive", () =>
    fc.assert(fc.property(arbitraryMoney, arbitraryMoney, arbitraryMoney, (x, y, z) => {
        if (isEqual(x, y) && isEqual(y, z)) {
            expect(isEqual(x, z)).toBe(true);
        }
    }))
);
```

**Tests Unitarios:**

```typescript
test("valores iguales de diferentes factories son iguales", () => {
    const a = makeMoney(100n, makeCurrency("USD"));
    const b = makeMoney(100n, makeCurrency("USD"));

    // Objetos diferentes, mismos valores
    expect(a).not.toBe(b);  // Desigualdad por referencia
    expect(isEqual(a, b)).toBe(true);  // Igualdad por valor
});

test("valores diferentes no son iguales", () => {
    const a = makeMoney(100n, makeCurrency("USD"));
    const b = makeMoney(200n, makeCurrency("USD"));

    expect(isEqual(a, b)).toBe(false);
});
```

---

### 9. Patrones de Inmutabilidad

**Regla:** Todas las estructuras de datos DEBEN ser readonly e inmutables.

**Tipos Readonly:**

```typescript
export type Order = Readonly<{
    kind: "Order",
    id: OrderId,
    items: ReadonlyArray<OrderItem>,
    total: Money
}>;

// O usa modificadores readonly
export type Order = {
    readonly kind: "Order",
    readonly id: OrderId,
    readonly items: ReadonlyArray<OrderItem>,
    readonly total: Money
};
```

**Copiado Defensivo en Factories:**

```typescript
export function makeOrder(
    id: OrderId,
    items: ReadonlyArray<OrderItem>
): Order {
    // Copia defensiva para evitar compartir referencias mutables
    const itemsCopy: OrderItem[] = items.slice();

    return {
        kind: "Order",
        id,
        items: Object.freeze(itemsCopy),  // Inmutabilidad en runtime
        total: calculateTotal(itemsCopy)
    };
}
```

**Operaciones de Actualización Devuelven Nuevas Instancias:**

```typescript
export function addItem(order: Order, item: OrderItem): Order {
    // Nunca mutar - crear nueva instancia mediante factory
    return makeOrder(order.id, [...order.items, item]);
}
```

---

## Estrategia de Testing

### Enfoque de Testing de Dos Niveles (OBLIGATORIO)

Cada funcionalidad de dominio DEBE tener ambos:

1. **Tests Unitarios** (`test/unit/`): Tests basados en ejemplos para escenarios específicos
2. **Tests Basados en Propiedades** (`test/pbt/`): Testing generativo para invariantes usando `fast-check`

### Estructura de Test Unitario

```typescript
import { describe, test, expect } from "vitest";
import { makeOrder, makeOrderItem } from "../../src/order/order.make.js";

describe("Order.addItem (unit)", () => {
    test("añade item y recalcula total", () => {
        const order = makeOrder(makeOrderId("1"), []);
        const item = makeOrderItem("Widget", 100n);

        const updated = addItem(order, item);

        expect(updated.items).toHaveLength(1);
        expect(updated.total.amount).toBe(100n);
    });

    test("inmutabilidad: order original sin cambios", () => {
        const order = makeOrder(makeOrderId("1"), []);
        const item = makeOrderItem("Widget", 100n);
        const before = { ...order };

        const updated = addItem(order, item);

        expect(order).toEqual(before);
        expect(updated).not.toBe(order);
    });

    test("lanza error en item inválido", () => {
        const order = makeOrder(makeOrderId("1"), []);

        expect(() => addItem(order, null as any)).toThrow(InvalidOrderItemError);
    });
});
```

### Estructura de Test Basado en Propiedades

```typescript
import fc from "fast-check";

const arbitraryAmount = fc.bigInt({ min: 0n, max: 1_000_000n });
const arbitraryItem = fc.record({ name: fc.string({ minLength: 1 }), price: arbitraryAmount });

// Testear propiedades algebraicas
test("total del order equivale a suma de precios de items", () =>
    fc.assert(fc.property(fc.array(arbitraryItem, { minLength: 1 }), (items) => {
        const order = makeOrder(makeOrderId("1"), items);
        const expectedTotal = items.reduce((sum, item) => sum + item.price, 0n);
        expect(order.total.amount).toBe(expectedTotal);
    }))
);
```

### Checklist de Tests

**Relaciones de Equivalencia:** Reflexividad, Simetría, Transitividad
**Propiedades Algebraicas:** Conmutatividad, Asociatividad, Identidad (si aplica)
**Invariantes de Dominio:** Closure, Inmutabilidad, Type safety, Determinismo, Consistencia Guard/Factory

---

## Configuración de TypeScript y Build

### tsconfig.json (configuración OBLIGATORIA)

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

### package.json (scripts recomendados)

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

### vitest.config.ts (configuración recomendada)

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
        "src/**/*.types.ts",   // Tipos puros: sin código runtime
        "src/**/index.ts",     // Archivos barrel
        "test/**",
      ],
    },
  },
});
```

---

## Convenciones Importantes

### ES Modules (OBLIGATORIO)

- El proyecto DEBE usar `"type": "module"` en package.json
- Todos los imports DEBEN incluir extensiones `.js` incluso para archivos `.ts`
- Ejemplo: `import { User } from "./user.types.js";`

### Precisión Numérica (para cálculos financieros/precisos)

- Usa `bigint` para aritmética entera precisa (dinero, cantidades)
- Nunca uses `number` o punto flotante para cálculos financieros
- Sintaxis literal: `42n` (nota el sufijo `n`)
- ADVERTENCIA: `1 !== 1n` en JavaScript

### Inmutabilidad (OBLIGATORIO)

- Todos los objetos de dominio DEBEN ser `readonly`
- Usa `ReadonlyArray<T>` para arrays
- Usa `Readonly<{...}>` para tipos de objeto
- Haz copias defensivas en funciones factory
- Las operaciones DEBEN devolver nuevas instancias, nunca mutar

### Normalización (RECOMENDADO)

- Normaliza datos de input antes de validación
- Normalizaciones comunes: trim, lowercase, uppercase
- Aplica consistentemente en todas las factories

### Type Checking en Tests

- Todos los comandos de test DEBERÍAN ejecutar typecheck antes de ejecutarse
- Usa `pnpm test:only` para omitir typechecking (iteración más rápida durante desarrollo)

---

## Añadir una Nueva Funcionalidad de Dominio

Al añadir una nueva funcionalidad, sigue este checklist:

### 1. Crear Archivos de Dominio

```text
src/<domain>/
├── <domain>.types.ts      # Define tipos primero
├── <domain>.make.ts       # Funciones factory
├── <domain>.guard.ts      # Type guards
├── <domain>.ops.ts        # Operaciones
├── <domain>.errors.ts     # Errores personalizados
└── <domain>.dto.*.ts      # DTOs si se necesitan para persistencia
```

### 2. Definir Tipos (`*.types.ts`)

- [ ] Usar discriminated union con campo `kind`
- [ ] Hacer todos los campos `readonly`
- [ ] Usar branded types si se necesita tipado nominal
- [ ] Definir sum types si existen múltiples variantes

### 3. Crear Factory (`*.make.ts`)

- [ ] VALIDAR todos los inputs usando type guards
- [ ] Lanzar errores descriptivos en input inválido
- [ ] Castear a branded type SOLO después de validación
- [ ] Crear factories de conveniencia para casos comunes
- [ ] Hacer copias defensivas de inputs mutables
- [ ] Usar `Object.freeze()` para inmutabilidad en runtime

### 4. Añadir Guards (`*.guard.ts`)

- [ ] Usar tipo de retorno type predicate (`x is Type`)
- [ ] Comprobar discriminador `kind` primero (si se usan discriminated unions)
- [ ] Validar TODOS los campos requeridos
- [ ] Componer con guards existentes
- [ ] Testear con property-based tests que `is*(make*(...)) === true`

### 5. Implementar Operaciones (`*.ops.ts`)

- [ ] Definir overloads type-safe para operaciones polimórficas
- [ ] Implementar dispatch polimórfico si se necesita
- [ ] Asegurar inmutabilidad (NUNCA mutar)
- [ ] Devolver nuevas instancias mediante factories
- [ ] Validar inputs usando guards

### 6. Definir Errores (`*.errors.ts`)

- [ ] Extender clase base `AppError`
- [ ] Incluir metadatos `userInfo` significativos
- [ ] Soportar encadenamiento de errores mediante parámetro `previous`
- [ ] Proporcionar mensajes de error útiles

### 7. Escribir Tests

**Tests unitarios** (`test/unit/<domain>.<feature>.unit.test.ts`):

- [ ] Testear caminos felices con ejemplos
- [ ] Testear condiciones de error
- [ ] Testear inmutabilidad
- [ ] Testear casos extremos

**Tests basados en propiedades** (`test/pbt/<domain>.<feature>.pbt.test.ts`):

- [ ] Testear propiedades algebraicas (si aplica)
- [ ] Testear relaciones de equivalencia
- [ ] Testear invariantes de dominio
- [ ] Testear determinismo
- [ ] Testear consistencia guard/factory

### 8. Actualizar Exports (si se usan barrel files)

- [ ] Exportar tipos desde `*.types.ts`
- [ ] Exportar factories desde `*.make.ts`
- [ ] Exportar guards desde `*.guard.ts`
- [ ] Exportar operaciones desde `*.ops.ts`

---

## Resumen de Principios Clave

1. **Estrategia de Tipos Híbrida**: Usa branded types para primitivos validados simples (Currency, EmailAddress, UserId) y discriminated unions para entidades de dominio complejas (Money, Order, User)
2. **Validación en Runtime**: Todas las factories DEBEN validar inputs antes de crear objetos
3. **Inmutabilidad en Todas Partes**: Todas las estructuras de datos son readonly y nunca se mutan
4. **Patrón Factory**: Todos los objetos creados mediante funciones factory validadas
5. **Type Narrowing**: Usa discriminador `kind` para entidades, branded types preservan parámetros genéricos para primitivos
6. **Funciones Guard**: Validación en runtime con type predicates para cada tipo de dominio
7. **Errores Estructurados**: Extender AppError con metadatos
8. **Testing de Dos Niveles**: Tests unitarios + tests basados en propiedades para cada funcionalidad
9. **Organización de Archivos**: Nomenclatura consistente (`*.types`, `*.make`, `*.guard`, `*.ops`, `*.errors`)
10. **ES Modules**: Usa extensiones `.js` en imports
