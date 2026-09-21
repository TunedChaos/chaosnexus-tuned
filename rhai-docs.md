

# arrays-oob.md
Out-of-Bounds Index for Arrays
==============================

{{#include ../links.md}}

[`Engine::on_invalid_array_index`]: https://docs.rs/rhai/{{version}}/rhai/struct.Engine.html#method.on_invalid_array_index
[`Target`]: https://docs.rs/rhai/latest/rhai/enum.Target.html


~~~admonish warning.small "Requires `internals`"

This is an advanced feature that requires the [`internals`] feature to be enabled.
~~~

Normally, when an index is out-of-bounds for an [array], an error is raised.

It is possible to completely control this behavior via a special callback function
registered into an [`Engine`] via `on_invalid_array_index`.

Using this callback, for instance, it is simple to instruct Rhai to extend the [array] to
accommodate this new element, or to return a default value instead of raising an error.


Function Signature
------------------

The function signature passed to [`Engine::on_invalid_array_index`] takes the following form.

> ```rust
> Fn(array: &mut Array, index: i64, context: EvalContext) -> Result<Target, Box<EvalAltResult>>
> ```

where:

| Parameter |         Type          | Description                      |
| --------- | :-------------------: | -------------------------------- |
| `array`   | [`&mut Array`][array] | the [array] being accessed       |
| `index`   |         `i64`         | index value                      |
| `context` |    [`EvalContext`]    | the current _evaluation context_ |

### Return value

The return value is `Result<Target, Box<EvalAltResult>>`.

[`Target`] is an advanced type, available only under the [`internals`] feature, that represents a
_reference_ to a [`Dynamic`] value.

It can be used to point to a particular value within the [array] or a new temporary value.


Example
-------

```rust
engine.on_invalid_array_index(|arr, index, _| {
    match index {
        -100 => {
            // The array can be modified in place
            arr.push((42_i64).into());

            // Return a mutable reference to an element
            let value_ref = arr.last_mut().unwrap();
            Ok(value_ref.into())
        }
        100 => {
            // Return a temporary value (not a reference)
            let value = Dynamic::from(100_i64);
            Ok(value.into())
        }
        // Return the standard out-of-bounds error
        _ => Err(EvalAltResult::ErrorArrayBounds(
                arr.len(), index, Position::NONE
             ).into()),
    }
});
```


# arrays.md
Arrays
======

{{#include ../links.md}}

```admonish tip.side "Safety"

Always limit the [maximum size of arrays].
```

Arrays are first-class citizens in Rhai.

All elements stored in an array are [`Dynamic`], and the array can freely grow or shrink with
elements added or removed.

The Rust type of a Rhai array is `rhai::Array` which is an alias to `Vec<Dynamic>`.

[`type_of()`] an array returns `"array"`.

Arrays are disabled via the [`no_index`] feature.


Literal Syntax
--------------

Array literals are built within square brackets `[` ... `]` and separated by commas `,`:

> `[` _value_`,` _value_`,` ... `,` _value_ `]`
>
> `[` _value_`,` _value_`,` ... `,` _value_ `,` `]`     `// trailing comma is OK`


Element Access Syntax
---------------------

### From beginning

Like C, arrays are accessed with zero-based, non-negative integer indices:

> _array_ `[` _index position from 0 to (length−1)_ `]`

### From end

A _negative_ position accesses an element in the array counting from the _end_, with −1 being the
_last_ element.

> _array_ `[` _index position from −1 to −length_ `]`


Out-of-Bounds Index
-------------------

Trying to read from an index that is out of bounds causes an error.

```admonish tip.small "Advanced tip: Override standard behavior"

For fine-tuned control on what happens when an out-of-bounds index is accessed,
see [_Out-of-Bounds Index for Arrays_](arrays-oob.md).
```

Built-in Functions
------------------

The following methods (mostly defined in the [`BasicArrayPackage`][built-in packages] but excluded
when using a [raw `Engine`]) operate on arrays.

| Function                       | Parameter(s)                                                                                                                                                   | Description                                                                                                                                                                                                                                                                                                               |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get`                          | position, counting from end if < 0                                                                                                                             | gets a copy of the element at a certain position ([`()`] if the position is not valid)                                                                                                                                                                                                                                    |
| `set`                          | <ol><li>position, counting from end if < 0</li><li>new element</li></ol>                                                                                       | sets a certain position to a new value (no effect if the position is not valid)                                                                                                                                                                                                                                           |
| `push`, `+=` operator          | element to append (not an array)                                                                                                                               | appends an element to the end                                                                                                                                                                                                                                                                                             |
| `append`, `+=` operator        | array to append                                                                                                                                                | concatenates the second array to the end of the first                                                                                                                                                                                                                                                                     |
| `+` operator                   | <ol><li>first array</li><li>second array</li></ol>                                                                                                             | concatenates the first array with the second                                                                                                                                                                                                                                                                              |
| `==` operator                  | <ol><li>first array</li><li>second array</li></ol>                                                                                                             | are two arrays the same (elements compared with the `==` operator, if defined)?                                                                                                                                                                                                                                           |
| `!=` operator                  | <ol><li>first array</li><li>second array</li></ol>                                                                                                             | are two arrays different (elements compared with the `==` operator, if defined)?                                                                                                                                                                                                                                          |
| `insert`                       | <ol><li>position, counting from end if < 0, end if ≥ length</li><li>element to insert</li></ol>                                                                | inserts an element at a certain position                                                                                                                                                                                                                                                                                  |
| `pop`                          | _none_                                                                                                                                                         | removes the last element and returns it ([`()`] if empty)                                                                                                                                                                                                                                                                 |
| `shift`                        | _none_                                                                                                                                                         | removes the first element and returns it ([`()`] if empty)                                                                                                                                                                                                                                                                |
| `extract`                      | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>_(optional)_ number of elements to extract, none if ≤ 0, to end if omitted</li></ol> | extracts a portion of the array into a new array                                                                                                                                                                                                                                                                          |
| `extract`                      | [range] of elements to extract, from beginning if ≤ 0, to end if ≥ length                                                                                      | extracts a portion of the array into a new array                                                                                                                                                                                                                                                                          |
| `remove`                       | position, counting from end if < 0                                                                                                                             | removes an element at a particular position and returns it ([`()`] if the position is not valid)                                                                                                                                                                                                                          |
| `reverse`                      | _none_                                                                                                                                                         | reverses the array                                                                                                                                                                                                                                                                                                        |
| `len` method and property      | _none_                                                                                                                                                         | returns the number of elements                                                                                                                                                                                                                                                                                            |
| `is_empty` method and property | _none_                                                                                                                                                         | returns `true` if the array is empty                                                                                                                                                                                                                                                                                      |
| `pad`                          | <ol><li>target length</li><li>element to pad</li></ol>                                                                                                         | pads the array with an element to at least a specified length                                                                                                                                                                                                                                                             |
| `clear`                        | _none_                                                                                                                                                         | empties the array                                                                                                                                                                                                                                                                                                         |
| `truncate`                     | target length                                                                                                                                                  | cuts off the array at exactly a specified length (discarding all subsequent elements)                                                                                                                                                                                                                                     |
| `chop`                         | target length                                                                                                                                                  | cuts off the head of the array, leaving the tail at exactly a specified length                                                                                                                                                                                                                                            |
| `split`                        | <ol><li>array</li><li>position to split at, counting from end if < 0, end if ≥ length</li></ol>                                                                | splits the array into two arrays, starting from a specified position                                                                                                                                                                                                                                                      |
| `for_each`                     | [function pointer] for processing elements                                                                                                                     | run through each element in the array in order, binding each to `this` and calling the processing function taking the following parameters: <ol><li>`this`: array element</li><li>_(optional)_ index position</li></ol>                                                                                                   |
| `drain`                        | [function pointer] to predicate (usually a [closure])                                                                                                          | removes all elements (returning them) that return `true` when called with the predicate function taking the following parameters (if none, the array element is bound to `this`):<ol><li>array element</li><li>_(optional)_ index position</li></ol>                                                                      |
| `drain`                        | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of elements to remove, none if ≤ 0</li></ol>                                  | removes a portion of the array, returning the removed elements as a new array                                                                                                                                                                                                                                             |
| `drain`                        | [range] of elements to remove, from beginning if ≤ 0, to end if ≥ length                                                                                       | removes a portion of the array, returning the removed elements as a new array                                                                                                                                                                                                                                             |
| `retain`                       | [function pointer] to predicate (usually a [closure])                                                                                                          | removes all elements (returning them) that do not return `true` when called with the predicate function taking the following parameters (if none, the array element is bound to `this`):<ol><li>array element</li><li>_(optional)_ index position</li></ol>                                                               |
| `retain`                       | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of elements to retain, none if ≤ 0</li></ol>                                  | retains a portion of the array, removes all other elements and returning them as a new array                                                                                                                                                                                                                              |
| `retain`                       | [range] of elements to retain, from beginning if ≤ 0, to end if ≥ length                                                                                       | retains a portion of the array, removes all other bytes and returning them as a new array                                                                                                                                                                                                                                 |
| `splice`                       | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of elements to remove, none if ≤ 0</li><li>array to insert</li></ol>          | replaces a portion of the array with another (not necessarily of the same length as the replaced portion)                                                                                                                                                                                                                 |
| `splice`                       | <ol><li>[range] of elements to remove, from beginning if ≤ 0, to end if ≥ length</li><li>array to insert</li></ol>                                             | replaces a portion of the array with another (not necessarily of the same length as the replaced portion)                                                                                                                                                                                                                 |
| `filter`                       | [function pointer] to predicate (usually a [closure])                                                                                                          | constructs a new array with all elements that return `true` when called with the predicate function taking the following parameters (if none, the array element is bound to `this`):<ol><li>array element</li><li>_(optional)_ index position</li></ol>                                                                   |
| `contains`, [`in`] operator    | element to find                                                                                                                                                | does the array contain an element? The `==` operator (if defined) is used to compare [custom types]                                                                                                                                                                                                                       |
| `index_of`                     | <ol><li>element to find (not a [function pointer])</li><li>_(optional)_ start position, counting from end if < 0, end if ≥ length</li></ol>                    | returns the position of the first element in the array that equals the supplied element (using the `==` operator, if defined), or −1 if not found</li></ol>                                                                                                                                                               |
| `index_of`                     | <ol><li>[function pointer] to predicate (usually a [closure])</li><li>_(optional)_ start position, counting from end if < 0, end if ≥ length</li></ol>         | returns the position of the first element in the array that returns `true` when called with the predicate function, or −1 if not found:<ol><li>array element (if none, the array element is bound to `this`)</li><li>_(optional)_ index position</li></ol>                                                                |
| `find`                         | <ol><li>[function pointer] to predicate (usually a [closure])</li><li>_(optional)_ start position, counting from end if < 0, end if ≥ length</li></ol>         | returns the first element in the array that returns `true` when called with the predicate function, or [`()`] if not found:<ol><li>array element (if none, the array element is bound to `this`)</li><li>_(optional)_ index position</li></ol>                                                                            |
| `find_map`                     | <ol><li>[function pointer] to predicate (usually a [closure])</li><li>_(optional)_ start position, counting from end if < 0, end if ≥ length</li></ol>         | returns the first non-[`()`] value of the first element in the array when called with the predicate function, or [`()`] if not found:<ol><li>array element (if none, the array element is bound to `this`)</li><li>_(optional)_ index position</li></ol>                                                                  |
| `dedup`                        | _(optional)_ [function pointer] to predicate (usually a [closure]); if omitted, the `==` operator is used, if defined                                          | removes all but the first of _consecutive_ elements in the array that return `true` when called with the predicate function (non-consecutive duplicates are _not_ removed):<br/>1st & 2nd parameters: two elements in the array                                                                                           |
| `map`                          | [function pointer] to conversion function (usually a [closure])                                                                                                | constructs a new array with all elements mapped to the result of applying the conversion function taking the following parameters (if none, the array element is bound to `this`):<ol><li>array element</li><li>_(optional)_ index position</li></ol>                                                                     |
| `reduce`                       | <ol><li>[function pointer] to accumulator function (usually a [closure])</li><li>_(optional)_ the initial value</li></ol>                                      | reduces the array into a single value via the accumulator function taking the following parameters (if the second parameter is omitted, the array element is bound to `this`):<ol><li>accumulated value ([`()`] initially)</li><li>`this`: array element</li><li>_(optional)_ index position</li></ol>                    |
| `reduce_rev`                   | <ol><li>[function pointer] to accumulator function (usually a [closure])</li><li>_(optional)_ the initial value</li></ol>                                      | reduces the array (in reverse order) into a single value via the accumulator function taking the following parameters (if the second parameter is omitted, the array element is bound to `this`):<ol><li>accumulated value ([`()`] initially)</li><li>`this`: array element</li><li>_(optional)_ index position</li></ol> |
| `zip`                          | <ol><li>array to zip</li><li>[function pointer] to conversion function (usually a [closure])</li></ol>                                                         | constructs a new array with all element pairs from two arrays mapped to the result of applying the conversion function taking the following parameters:<ol><li>first array element</li><li>second array element</li><li>_(optional)_ index position</li></ol>                                                             |
| `some`                         | [function pointer] to predicate (usually a [closure])                                                                                                          | returns `true` if any element returns `true` when called with the predicate function taking the following parameters (if none, the array element is bound to `this`):<ol><li>array element</li><li>_(optional)_ index position</li></ol>                                                                                  |
| `all`                          | [function pointer] to predicate (usually a [closure])                                                                                                          | returns `true` if all elements return `true` when called with the predicate function taking the following parameters (if none, the array element is bound to `this`):<ol><li>array element</li><li>_(optional)_ index position</li></ol>                                                                                  |
| `sort_by`                      | [function pointer] to a comparison function (usually a [closure])                                                                                              | sorts the array with a comparison function taking the following parameters:<ol><li>first element</li><li>second element<br/>return value: `INT` < 0 if first < second, > 0 if first > second, 0 if first == second</li></ol>                                                                                              |
| `sort`                         | _none_                                                                                                                                                         | sorts a _homogeneous_ array containing only elements of the same comparable built-in type (`INT`, `FLOAT`, [`Decimal`][rust_decimal], [string], [character], `bool`, [`()`])                                                                                                                                              |
| `sort_desc`                    | _none_                                                                                                                                                         | sorts, in descending order, a _homogeneous_ array containing only elements of the same comparable built-in type (`INT`, `FLOAT`, [`Decimal`][rust_decimal], [string], [character], `bool`, [`()`])                                                                                                                        |
| `order_by`                     | [function pointer] to a comparison function (usually a [closure])                                                                                              | returns a copy of the array that is sorted with a comparison function taking the following parameters:<ol><li>first element</li><li>second element<br/>return value: `INT` < 0 if first < second, > 0 if first > second, 0 if first == second</li></ol>                                                                   |
| `order`                        | _none_                                                                                                                                                         | returns a sorted copy of a _homogeneous_ array containing only elements of the same comparable built-in type (`INT`, `FLOAT`, [`Decimal`][rust_decimal], [string], [character], `bool`, [`()`])                                                                                                                           |
| `order_desc`                   | _none_                                                                                                                                                         | returns a sorted (in descending order) copy of a _homogeneous_ array containing only elements of the same comparable built-in type (`INT`, `FLOAT`, [`Decimal`][rust_decimal], [string], [character], `bool`, [`()`])                                                                                                     |


```admonish tip.small "Tip: Use custom types with arrays"

To use a [custom type] with arrays, a number of functions need to be manually implemented,
in particular the `==` operator in order to support the [`in`] operator which uses `==` (via the
`contains` method) to compare elements.

See the section on [custom types] for more details.
```


Examples
--------

```rust
let y = [2, 3];             // y == [2, 3]

let y = [2, 3,];            // y == [2, 3]

y.insert(0, 1);             // y == [1, 2, 3]

y.insert(999, 4);           // y == [1, 2, 3, 4]

y.len == 4;

y[0] == 1;
y[1] == 2;
y[2] == 3;
y[3] == 4;

(1 in y) == true;           // use 'in' to test if an element exists in the array

(42 in y) == false;         // 'in' uses the 'contains' function, which uses the
                            // '==' operator (that users can override)
                            // to check if the target element exists in the array

y.contains(1) == true;      // the above de-sugars to this

y[1] = 42;                  // y == [1, 42, 3, 4]

(42 in y) == true;

y.remove(2) == 3;           // y == [1, 42, 4]

y.len == 3;

y[2] == 4;                  // elements after the removed element are shifted

ts.list = y;                // arrays can be assigned completely (by value copy)

ts.list[1] == 42;

[1, 2, 3][0] == 1;          // indexing on array literal

[1, 2, 3][-1] == 3;         // negative position counts from the end

fn abc() {
    [42, 43, 44]            // a function returning an array
}

abc()[0] == 42;

y.push(4);                  // y == [1, 42, 4, 4]

y += 5;                     // y == [1, 42, 4, 4, 5]

y.len == 5;

y.shift() == 1;             // y == [42, 4, 4, 5]

y.chop(3);                  // y == [4, 4, 5]

y.len == 3;

y.pop() == 5;               // y == [4, 4]

y.len == 2;

for element in y {          // arrays can be iterated with a 'for' statement
    print(element);
}

y.pad(6, "hello");          // y == [4, 4, "hello", "hello", "hello", "hello"]

y.len == 6;

y.truncate(4);              // y == [4, 4, "hello", "hello"]

y.len == 4;

y.clear();                  // y == []

y.len == 0;

// The examples below use 'a' as the master array

let a = [42, 123, 99];

a.for_each(|| this *= 2);

a == [84, 246, 198];

a.for_each(|i| this /= 2);

a == [42, 123, 99];

a.map(|v| v + 1);           // returns [43, 124, 100]

a.map(|| this + 1);         // returns [43, 124, 100]

a.map(|v, i| v + i);        // returns [42, 124, 101]

a.filter(|v| v > 50);       // returns [123, 99]

a.filter(|| this > 50);     // returns [123, 99]

a.filter(|v, i| i == 1);    // returns [123]

a.filter("is_odd");         // returns [123, 99]

a.filter(Fn("is_odd"));     // <- previous statement is equivalent to this...

a.filter(|v| is_odd(v));    // <- or this

a.some(|v| v > 50);         // returns true

a.some(|| this > 50);       // returns true

a.some(|v, i| v < i);       // returns false

a.all(|v| v > 50);          // returns false

a.all(|| this > 50);        // returns false

a.all(|v, i| v > i);        // returns true

// Reducing - initial value provided directly
a.reduce(|sum| sum + this, 0) == 264;

// Reducing - initial value provided directly
a.reduce(|sum, v| sum + v, 0) == 264;

// Reducing - initial value is '()'
a.reduce(
    |sum, v| if sum.type_of() == "()" { v } else { sum + v }
) == 264;

// Reducing - initial value has index position == 0
a.reduce(|sum, v, i|
    if i == 0 { v } else { sum + v }
) == 264;

// Reducing in reverse - initial value provided directly
a.reduce_rev(|sum| sum + this, 0) == 264;

// Reducing in reverse - initial value provided directly
a.reduce_rev(|sum, v| sum + v, 0) == 264;

// Reducing in reverse - initial value is '()'
a.reduce_rev(
    |sum, v| if sum.type_of() == "()" { v } else { sum + v }
) == 264;

// Reducing in reverse - initial value has index position == 0
a.reduce_rev(|sum, v, i|
    if i == 2 { v } else { sum + v }
) == 264;

// In-place modification

a.splice(1..=1, [1, 3, 2]); // a == [42, 1, 3, 2, 99]

a.extract(1..=3);           // returns [1, 3, 2]

a.sort(|x, y| y - x);       // a == [99, 42, 3, 2, 1]

a.sort();                   // a == [1, 2, 3, 42, 99]

a.drain(|v| v <= 1);        // a == [2, 3, 42, 99]

a.drain(|v, i| i ≥ 3);      // a == [2, 3, 42]

a.retain(|v| v > 10);       // a == [42]

a.retain(|v, i| i > 0);     // a == []
```


# assignment-op.md
Compound Assignments
====================

{{#include ../links.md}}


Compound assignments are assignments with a [binary operator][operators] attached.

```rust
number += 8;            // number = number + 8

number -= 7;            // number = number - 7

number *= 6;            // number = number * 6

number /= 5;            // number = number / 5

number %= 4;            // number = number % 4

number **= 3;           // number = number ** 3

number <<= 2;           // number = number << 2

number >>= 1;           // number = number >> 1

number &= 0x00ff;       // number = number & 0x00ff;

number |= 0x00ff;       // number = number | 0x00ff;

number ^= 0x00ff;       // number = number ^ 0x00ff;
```


The Flexible `+=`
-----------------

The the `+` and `+=` operators are often [overloaded][function overloading] to perform build-up
operations for different data types.

### Build strings

```rust
let my_str = "abc";

my_str += "ABC";
my_str += 12345;

my_str == "abcABC12345"
```

### Concatenate arrays

```rust
let my_array = [1, 2, 3];

my_array += [4, 5];

my_array == [1, 2, 3, 4, 5];
```

### Concatenate BLOB's

```rust
let my_blob = blob(3, 0x42);

my_blob += blob(5, 0x89);

my_blob.to_string() == "[4242428989898989]";
```

### Mix two object maps together

```rust
let my_obj = #{ a:1, b:2 };

my_obj += #{ c:3, d:4, e:5 };

my_obj == #{ a:1, b:2, c:3, d:4, e:5 };
```

### Add seconds to timestamps

```rust
let now = timestamp();

now += 42.0;

(now - timestamp()).round() == 42.0;
```


# assignment.md
Assignments
===========

{{#include ../links.md}}

Value assignments to [variables] use the `=` symbol.

```rust
let foo = 42;

bar = 123 * 456 - 789;

x[1][2].prop = do_calculation();
```


Valid Assignment Targets
------------------------

The left-hand-side (LHS) of an assignment statement must be a valid
_[l-value](https://en.wikipedia.org/wiki/Value_(computer_science))_, which must be rooted in a
[variable], potentially extended via indexing or properties.

~~~admonish bug "Assigning to invalid l-value"

Expressions that are not valid _l-values_ cannot be assigned to.

```rust
x = 42;                 // variable is an l-value

x[1][2][3] = 42         // variable indexing is an l-value

x.prop1.prop2 = 42;     // variable property is an l-value

foo(x) = 42;            // syntax error: function call is not an l-value

x.foo() = 42;           // syntax error: method call is not an l-value

(x + y) = 42;           // syntax error: binary op is not an l-value
```
~~~


Values are Cloned
-----------------

Values assigned are always _cloned_.
So care must be taken when assigning large data types (such as [arrays]).

```rust
x = y;                  // value of 'y' is cloned

x == y;                 // both 'x' and 'y' hold different copies
                        // of the same value
```


Moving Data
-----------

When assigning large data types, sometimes it is desirable to _move_ the data instead of cloning it.

Use the `take` function (defined in the [`LangCorePackage`][built-in packages] but excluded
when using a [raw `Engine`]) to _move_ data.

### The original variable is left with `()`

```rust
x = take(y);            // value of 'y' is moved to 'x'

y == ();                // 'y' now holds '()'

x != y;                 // 'x' holds the original value of 'y'
```

### Return large data types from functions

`take` is convenient when returning large data types from a [function].

```rust
fn get_large_value_naive() {
    let large_result = do_complex_calculation();

    large_result.done = true;

    // Return a cloned copy of the result, then the
    // local variable 'large_result' is thrown away!
    large_result
}

fn get_large_value_smart() {
    let large_result = do_complex_calculation();

    large_result.done = true;

    // Return the result without cloning!
    // Method style call is also OK.
    large_result.take()
}
```

### Assigning large data types to object map properties

`take` is useful when assigning large data types to [object map] properties.

```rust
let x = [];

// Build a large array
for n in 0..1000000 { x += n; }

// The following clones the large array from 'x'.
// Both 'my_object.my_property' and 'x' now hold exact copies
// of the same large array!
my_object.my_property = x;

// Move it to object map property via 'take' without cloning.
// 'x' now holds '()'.
my_object.my_property = x.take();

// Without 'take', the following must be done to avoid cloning:
my_object.my_property = [];

for n in 0..1000000 { my_object.my_property += n; }
```


# bit-fields.md
Integer as Bit-Fields
=====================

{{#include ../links.md}}

```admonish note.side

Nothing here cannot be done via standard bit-manipulation (i.e. shifting and masking).

Built-in support is more elegant and performant since it usually replaces a sequence of multiple steps.

```

Since bit-wise operators are defined on integer numbers, individual bits can also be accessed and
manipulated via an indexing syntax.

If a bit is set (i.e. `1`), the index access returns `true`.

If a bit is not set (i.e. `0`), the index access returns `false`.

When a [range] is used, the bits within the [range] are shifted and extracted as an integer value.

Bit-fields are very commonly used in embedded systems which must squeeze data into limited memory.
Built-in support makes handling them efficient.

Indexing an integer as a bit-field is disabled for the [`no_index`] feature.


Syntax
------

### From Least-Significant Bit (LSB)

Bits in a bit-field are accessed with zero-based, non-negative integer indices:

> _integer_ `[` _index from 0 to 63 or 31_ `]`
>
> _integer_ `[` _index from 0 to 63 or 31_ `] =` `true` or `false` ;

[Ranges] can also be used:

> _integer_ `[` _start_ `..` _end_ `]`  
> _integer_ `[` _start_ `..=` _end_ `]`
>
> _integer_ `[` _start_ `..` _end_ `] =` _new integer value_ ;  
> _integer_ `[` _start_ `..=` _end_ `] =` _new integer value_ ;

```admonish warning.small "Number of bits"

The maximum bit number that can be accessed is 63 (or 31 under [`only_i32`]).

Bits outside of the range are ignored.
```


### From Most-Significant Bit (MSB)

A _negative_ index accesses a bit in the bit-field counting from the _end_, or from the
_most-significant bit_, with −1 being the _highest_ bit.

> _integer_ `[` _index from −1 to −64 or −32_ `]`
>
> _integer_ `[` _index from −1 to −64 or −32_ `] =` `true` or `false` ;

[Ranges] always count from the least-significant bit (LSB) and has no support for negative positions.

```admonish warning.small "Number of bits"

The maximum bit number that can be accessed is −64 (or −32 under [`only_i32`]).
```


Bit-Field Functions
-------------------

The following standard functions (defined in the [`BitFieldPackage`][built-in packages] but excluded
when using a [raw `Engine`]) operate on `INT` bit-fields.

These functions are available even under the [`no_index`] feature.

| Function                   | Parameter(s)                                                                                                                                                   | Description                                               |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `get_bit`                  | bit number, counting from MSB if < 0                                                                                                                           | returns the state of a bit: `true` if `1`, `false` if `0` |
| `set_bit`                  | <ol><li>bit number, counting from MSB if < 0</li><li>new state: `true` if `1`, `false` if `0`</li></ol>                                                        | sets the state of a bit                                   |
| `get_bits`                 | <ol><li>starting bit number, counting from MSB if < 0</li><li>number of bits to extract, none if < 1, to MSB if ≥ _length_</li></ol>                           | extracts a number of bits, shifted towards LSB            |
| `get_bits`                 | [range] of bits                                                                                                                                                | extracts a number of bits, shifted towards LSB            |
| `set_bits`                 | <ol><li>starting bit number, counting from MSB if < 0</li><li>number of bits to set, none if < 1, to MSB if ≥ _length_<br/>3) new value</li></ol>              | sets a number of bits from the new value                  |
| `set_bits`                 | <ol><li>[range] of bits</li><li>new value</li></ol>                                                                                                            | sets a number of bits from the new value                  |
| `bits` method and property | <ol><li>_(optional)_ starting bit number, counting from MSB if < 0</li><li>_(optional)_ number of bits to extract, none if < 1, to MSB if ≥ _length_</li></ol> | allows iteration over the bits of a bit-field             |
| `bits`                     | [range] of bits                                                                                                                                                | allows iteration over the bits of a bit-field             |


Example
-------

```js , no_run
// Assume the following bits fields in a single 16-bit word:
// ┌─────────┬────────────┬──────┬─────────┐
// │  15-12  │    11-4    │  3   │   2-0   │
// ├─────────┼────────────┼──────┼─────────┤
// │    0    │ 0-255 data │ flag │ command │
// └─────────┴────────────┴──────┴─────────┘

let value = read_start_hw_register(42);

let command = value.get_bits(0, 3);         // Command = bits 0-2

let flag = value[3];                        // Flag = bit 3

let data = value[4..=11];                   // Data = bits 4-11
let data = value.get_bits(4..=11);          // <- above is the same as this

let reserved = value.get_bits(-4);          // Reserved = last 4 bits

if reserved != 0 {
    throw reserved;
}

switch command {
    0 => print(`Data = ${data}`),
    1 => value[4..=11] = data / 2,
    2 => value[3] = !flag,
    _ => print(`Unknown: ${command}`)
}
```


# blobs.md
BLOB's
======

{{#include ../links.md}}

```admonish tip.side "Safety"

Always limit the [maximum size of arrays].
```

BLOB's (**B**inary **L**arge **OB**jects), used to hold packed arrays of bytes, have built-in support in Rhai.

A BLOB has no literal representation, but is created via the `blob` function, or simply returned as
the result of a function call (e.g. `generate_thumbnail_image` that generates a thumbnail version of
a large image as a BLOB).

All items stored in a BLOB are bytes (i.e. `u8`) and the BLOB can freely grow or shrink with bytes
added or removed.

The Rust type of a Rhai BLOB is `rhai::Blob` which is an alias to `Vec<u8>`.

[`type_of()`] a BLOB returns `"blob"`.

BLOB's are disabled via the [`no_index`] feature.


Element Access Syntax
---------------------

### From beginning

Like [arrays], BLOB's are accessed with zero-based, non-negative integer indices:

> _blob_ `[` _index position from 0 to (length−1)_ `]`

### From end

A _negative_ position accesses an element in the BLOB counting from the _end_, with −1 being the
_last_ element.

> _blob_ `[` _index position from −1 to −length_ `]`

```admonish info.small "Byte values"

The value of a particular byte in a BLOB is mapped to an `INT` (which can be 64-bit or 32-bit
depending on the [`only_i32`] feature).

Only the lowest 8 bits are significant, all other bits are ignored.
```


Create a BLOB
-------------

The function `blob` allows creating an empty BLOB, optionally filling it to a required size with a
particular value (default zero).

```rust
let x = blob();             // empty BLOB

let x = blob(10);           // BLOB with ten zeros

let x = blob(50, 42);       // BLOB with 50x 42's
```

```admonish tip "Tip: Initialize with byte stream"

To quickly initialize a BLOB with a particular byte stream, the `write_be` method can be used to
write eight bytes at a time (four under [`only_i32`]) in big-endian byte order.

If fewer than eight bytes are needed, remember to right-pad the number as big-endian byte order is used.

~~~rust
let buf = blob(12, 0);      // BLOB with 12x zeros

// Write eight bytes at a time, in big-endian order
buf.write_be(0, 8, 0xab_cd_ef_12_34_56_78_90);
buf.write_be(8, 8, 0x0a_0b_0c_0d_00_00_00_00);
                            //   ^^^^^^^^^^^ remember to pad unused bytes

print(buf);                 // prints "[abcdef1234567890 0a0b0c0d]"

buf[3] == 0x12;
buf[10] == 0x0c;

// Under 'only_i32', write four bytes at a time:
buf.write_be(0, 4, 0xab_cd_ef_12);
buf.write_be(4, 4, 0x34_56_78_90);
buf.write_be(8, 4, 0x0a_0b_0c_0d);
~~~
```


Writing ASCII Bytes
-------------------

```admonish warning.side "Non-ASCII"

Non-ASCII characters (i.e. characters not within 1-127) are ignored.
```

For many embedded applications, it is necessary to encode an ASCII [string] as a byte stream.

Use the `write_ascii` method to write ASCII [strings] into any specific [range] within a BLOB.

The following is an example of a building a 16-byte command to send to an embedded device.

```rust
// Assume the following 16-byte command for an embedded device:
// ┌─────────┬───────────────┬──────────────────────────────────┬───────┐
// │    0    │       1       │              2-13                │ 14-15 │
// ├─────────┼───────────────┼──────────────────────────────────┼───────┤
// │ command │ string length │ ASCII string, max. 12 characters │  CRC  │
// └─────────┴───────────────┴──────────────────────────────────┴───────┘

let buf = blob(16, 0);      // initialize command buffer

let text = "foo & bar";     // text string to send to device

buf[0] = 0x42;              // command code
buf[1] = s.len();           // length of string

buf.write_ascii(2..14, text);   // write the string

let crc = buf.calc_crc();   // calculate CRC

buf.write_le(14, 2, crc);   // write CRC

print(buf);                 // prints "[4209666f6f202620 626172000000abcd]"
                            //          ^^ command code              ^^^^ CRC
                            //            ^^ string length
                            //              ^^^^^^^^^^^^^^^^^^^ foo & bar

device.send(buf);           // send command to device
```

```admonish question.small "What if I need UTF-8?"

The `write_utf8` function writes a string in UTF-8 encoding.

UTF-8, however, is not very common for embedded applications.
```


Built-in Functions
------------------

The following functions (mostly defined in the [`BasicBlobPackage`][built-in packages] but excluded
when using a [raw `Engine`]) operate on BLOB's.

| Functions                                               | Parameter(s)                                                                                                                                                                                                        | Description                                                                                                                                          |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `blob` constructor function                             | <ol><li>_(optional)_ initial length of the BLOB</li><li>_(optional)_ initial byte value</li></ol>                                                                                                                   | creates a new BLOB, optionally of a particular length filled with an initial byte value (default = 0)                                                |
| `to_array`                                              | _none_                                                                                                                                                                                                              | converts the BLOB into an [array] of integers                                                                                                        |
| `as_string`                                             | _none_                                                                                                                                                                                                              | converts the BLOB into a [string] (the byte stream is interpreted as UTF-8)                                                                          |
| `get`                                                   | position, counting from end if < 0                                                                                                                                                                                  | gets a copy of the byte at a certain position (0 if the position is not valid)                                                                       |
| `set`                                                   | <ol><li>position, counting from end if < 0</li><li>new byte value</li></ol>                                                                                                                                         | sets a certain position to a new value (no effect if the position is not valid)                                                                      |
| `push`, `append`, `+=` operator                         | <ol><li>BLOB</li><li>byte to append</li></ol>                                                                                                                                                                       | appends a byte to the end                                                                                                                            |
| `append`, `+=` operator                                 | <ol><li>BLOB</li><li>BLOB to append</li></ol>                                                                                                                                                                       | concatenates the second BLOB to the end of the first                                                                                                 |
| `append`, `+=` operator                                 | <ol><li>BLOB</li><li>[string]/[character] to append</li></ol>                                                                                                                                                       | concatenates a [string] or [character] (as UTF-8 encoded byte-stream) to the end of the BLOB                                                         |
| `+` operator                                            | <ol><li>first BLOB</li><li>[string] to append</li></ol>                                                                                                                                                             | creates a new [string] by concatenating the BLOB (as UTF-8 encoded byte-stream) with the the [string]                                                |
| `+` operator                                            | <ol><li>[string]</li><li>BLOB to append</li></ol>                                                                                                                                                                   | creates a new [string] by concatenating the BLOB (as UTF-8 encoded byte-stream) to the end of the [string]                                           |
| `+` operator                                            | <ol><li>first BLOB</li><li>second BLOB</li></ol>                                                                                                                                                                    | concatenates the first BLOB with the second                                                                                                          |
| `==` operator                                           | <ol><li>first BLOB</li><li>second BLOB</li></ol>                                                                                                                                                                    | are two BLOB's the same?                                                                                                                             |
| `!=` operator                                           | <ol><li>first BLOB</li><li>second BLOB</li></ol>                                                                                                                                                                    | are two BLOB's different?                                                                                                                            |
| `insert`                                                | <ol><li>position, counting from end if < 0, end if ≥ length</li><li>byte to insert</li></ol>                                                                                                                        | inserts a byte at a certain position                                                                                                                 |
| `pop`                                                   | _none_                                                                                                                                                                                                              | removes the last byte and returns it (0 if empty)                                                                                                    |
| `shift`                                                 | _none_                                                                                                                                                                                                              | removes the first byte and returns it (0 if empty)                                                                                                   |
| `extract`                                               | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>_(optional)_ number of bytes to extract, none if ≤ 0</li></ol>                                                                            | extracts a portion of the BLOB into a new BLOB                                                                                                       |
| `extract`                                               | [range] of bytes to extract, from beginning if ≤ 0, to end if ≥ length                                                                                                                                              | extracts a portion of the BLOB into a new BLOB                                                                                                       |
| `remove`                                                | position, counting from end if < 0                                                                                                                                                                                  | removes a byte at a particular position and returns it (0 if the position is not valid)                                                              |
| `reverse`                                               | _none_                                                                                                                                                                                                              | reverses the BLOB byte by byte                                                                                                                       |
| `len` method and property                               | _none_                                                                                                                                                                                                              | returns the number of bytes in the BLOB                                                                                                              |
| `is_empty` method and property                          | _none_                                                                                                                                                                                                              | returns `true` if the BLOB is empty                                                                                                                  |
| `pad`                                                   | <ol><li>target length</li><li>byte value to pad</li></ol>                                                                                                                                                           | pads the BLOB with a byte value to at least a specified length                                                                                       |
| `clear`                                                 | _none_                                                                                                                                                                                                              | empties the BLOB                                                                                                                                     |
| `truncate`                                              | target length                                                                                                                                                                                                       | cuts off the BLOB at exactly a specified length (discarding all subsequent bytes)                                                                    |
| `chop`                                                  | target length                                                                                                                                                                                                       | cuts off the head of the BLOB, leaving the tail at exactly a specified length                                                                        |
| `contains`, [`in`] operator                             | byte value to find                                                                                                                                                                                                  | does the BLOB contain a particular byte value?                                                                                                       |
| `split`                                                 | <ol><li>BLOB</li><li>position to split at, counting from end if < 0, end if ≥ length</li></ol>                                                                                                                      | splits the BLOB into two BLOB's, starting from a specified position                                                                                  |
| `drain`                                                 | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to remove, none if ≤ 0</li></ol>                                                                                          | removes a portion of the BLOB, returning the removed bytes as a new BLOB                                                                             |
| `drain`                                                 | [range] of bytes to remove, from beginning if ≤ 0, to end if ≥ length                                                                                                                                               | removes a portion of the BLOB, returning the removed bytes as a new BLOB                                                                             |
| `retain`                                                | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to retain, none if ≤ 0</li></ol>                                                                                          | retains a portion of the BLOB, removes all other bytes and returning them as a new BLOB                                                              |
| `retain`                                                | [range] of bytes to retain, from beginning if ≤ 0, to end if ≥ length                                                                                                                                               | retains a portion of the BLOB, removes all other bytes and returning them as a new BLOB                                                              |
| `splice`                                                | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to remove, none if ≤ 0</li><li>BLOB to insert</li></ol>                                                                   | replaces a portion of the BLOB with another (not necessarily of the same length as the replaced portion)                                             |
| `splice`                                                | <ol><li>[range] of bytes to remove, from beginning if ≤ 0, to end if ≥ length</li><li>BLOB to insert                                                                                                                | replaces a portion of the BLOB with another (not necessarily of the same length as the replaced portion)                                             |
| `parse_le_int`                                          | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to parse, 8 if > 8 (4 under [`only_i32`]), none if ≤ 0</li></ol>                                                          | parses an integer at the particular offset in little-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)              |
| `parse_le_int`                                          | [range] of bytes to parse, from beginning if ≤ 0, to end if ≥ length (up to 8 bytes, 4 under [`only_i32`])                                                                                                          | parses an integer at the particular offset in little-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)              |
| `parse_be_int`                                          | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to parse, 8 if > 8 (4 under [`only_i32`]), none if ≤ 0</li></ol>                                                          | parses an integer at the particular offset in big-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)                 |
| `parse_be_int`                                          | [range] of bytes to parse, from beginning if ≤ 0, to end if ≥ length (up to 8 bytes, 4 under [`only_i32`])                                                                                                          | parses an integer at the particular offset in big-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)                 |
| `parse_le_float`<br/>(not available under [`no_float`]) | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to parse, 8 if > 8 (4 under [`f32_float`]), none if ≤ 0</li></ol>                                                         | parses a floating-point number at the particular offset in little-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored) |
| `parse_le_float`<br/>(not available under [`no_float`]) | [range] of bytes to parse, from beginning if ≤ 0, to end if ≥ length (up to 8 bytes, 4 under [`f32_float`])                                                                                                         | parses a floating-point number at the particular offset in little-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored) |
| `parse_be_float`<br/>(not available under [`no_float`]) | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to parse, 8 if > 8 (4 under [`f32_float`]), none if ≤ 0</li></ol>                                                         | parses a floating-point number at the particular offset in big-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)    |
| `parse_be_float`<br/>(not available under [`no_float`]) | [range] of bytes to parse, from beginning if ≤ 0, to end if ≥ length (up to 8 bytes, 4 under [`f32_float`])                                                                                                         | parses a floating-point number at the particular offset in big-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)    |
| `write_le`                                              | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to write, 8 if > 8 (4 under [`only_i32`] or [`f32_float`]), none if ≤ 0</li><li>integer or floating-point value</li></ol> | writes a value at the particular offset in little-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)                 |
| `write_le`                                              | <ol><li>[range] of bytes to write, from beginning if ≤ 0, to end if ≥ length (up to 8 bytes, 4 under [`only_i32`] or [`f32_float`])</li><li>integer or floating-point value</li></ol>                               | writes a value at the particular offset in little-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)                 |
| `write_be`                                              | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to write, 8 if > 8 (4 under [`only_i32`] or [`f32_float`]), none if ≤ 0</li><li>integer or floating-point value</li></ol> | writes a value at the particular offset in big-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)                    |
| `write_be`                                              | <ol><li>[range] of bytes to write, from beginning if ≤ 0, to end if ≥ length (up to 8 bytes, 4 under [`only_i32`] or [`f32_float`])</li><li>integer or floating-point value</li></ol>                               | writes a value at the particular offset in big-endian byte order (if not enough bytes, zeros are padded; extra bytes are ignored)                    |
| `write_utf8`                                            | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of bytes to write, none if ≤ 0, to end if ≥ length</li><li>[string] to write</li></ol>                                             | writes a [string] to the particular offset in UTF-8 encoding                                                                                         |
| `write_utf8`                                            | <ol><li>[range] of bytes to write, from beginning if ≤ 0, to end if ≥ length, to end if ≥ length</li><li>[string] to write</li></ol>                                                                                | writes a [string] to the particular offset in UTF-8 encoding                                                                                         |
| `write_ascii`                                           | <ol><li>start position, counting from end if < 0, end if ≥ length</li><li>number of [characters] to write, none if ≤ 0, to end if ≥ length</li><li>[string] to write</li></ol>                                      | writes a [string] to the particular offset in 7-bit ASCII encoding (non-ASCII [characters] are skipped)                                              |
| `write_ascii`                                           | <ol><li>[range] of bytes to write, from beginning if ≤ 0, to end if ≥ length, to end if ≥ length</li><li>[string] to write</li></ol>                                                                                | writes a [string] to the particular offset in 7-bit ASCII encoding (non-ASCII [characters] are skipped)                                              |


# comments.md
Comments
========

{{#include ../links.md}}

Comments are C-style, including `/*` ... `*/` pairs for block comments and `//` for comments to the
end of the line.

Block comments can be nested.

```rust
let /* intruder comment */ name = "Bob";

// This is a very important one-line comment

/* This comment spans
   multiple lines, so it
   only makes sense that
   it is even more important */

/* Fear not, Rhai satisfies all nesting needs with nested comments:
   /*/*/*/*/**/*/*/*/*/
*/
```


Module Documentation
--------------------

Comment lines starting with `//!` make up the _module documentation_.

They are used to document the containing [module] &ndash; or for a Rhai script file,
to document the file itself.

~~~admonish warning.small "Requires `metadata`"

Module documentation is only supported under the [`metadata`] feature.

If [`metadata`] is not active, they are treated as normal [comments].
~~~

```rust
//! Documentation for this script file.
//! This script is used to calculate something and display the result.

fn calculate(x) {
   ...
}

fn display(msg) {
   //! Module documentation can be placed anywhere within the file.
   ...
}

//! All module documentation lines will be collected into a single block.
```

For the example above, the module documentation block is:

```rust
//! Documentation for this script file.
//! This script is used to calculate something and display the result.
//! Module documentation can be placed anywhere within the file.
//! All module documentation lines will be collected into a single block.
```


# constants.md
Constants
=========

{{#include ../links.md}}

Constants can be defined using the `const` keyword and are immutable.

```rust
const X;            // 'X' is a constant '()'

const X = 40 + 2;   // 'X' is a constant 42

print(X * 2);       // prints 84

X = 123;            // <- syntax error: constant modified
```

```admonish tip.small "Tip: Naming"

Constants follow the same naming rules as [variables], but as a convention are often named with
all-capital letters.
```


Manually Add Constant into Custom Scope
---------------------------------------

```admonish tip.side "Tip: Singleton"

A constant value holding a [custom type] essentially acts
as a [_singleton_]({{rootUrl}}/patterns/singleton.md).
```

It is possible to add a constant into a custom [`Scope`] via `Scope::push_constant` so it'll be
available to scripts running with that [`Scope`].

```rust
use rhai::{Engine, Scope};

#[derive(Debug, Clone)]
struct TestStruct(i64);                                     // custom type

let mut engine = Engine::new();

engine
    .register_type_with_name::<TestStruct>("TestStruct")    // register custom type
    .register_get("value", |obj: &mut TestStruct| obj.0),   // property getter
    .register_fn("update_value",
        |obj: &mut TestStruct, value: i64| obj.0 = value    // mutating method
    );

let script =
"
    MY_NUMBER.update_value(42);
    print(MY_NUMBER.value);
";

let ast = engine.compile(script)?;

let mut scope = Scope::new();                               // create custom scope

scope.push_constant("MY_NUMBER", TestStruct(123_i64));      // add constant variable

// Beware: constant objects can still be modified via a method call!
engine.run_ast_with_scope(&mut scope, &ast)?;               // prints 42

// Running the script directly, as below, is less desirable because
// the constant 'MY_NUMBER' will be propagated and copied into each usage
// during the script optimization step
engine.run_with_scope(&mut scope, script)?;
```


Caveat &ndash; Constants Can be Modified via Rust
-------------------------------------------------

```admonish tip.side.wide "Tip: Plugin functions"

In [plugin functions], `&mut` parameters disallow constant values by default.

This is different from the `Engine::register_XXX` API.

However, if a [plugin function] is marked with `#[export_fn(pure)]` or `#[rhai_fn(pure)]`,
it is assumed _pure_ (i.e. will not modify its arguments) and so constants are allowed.
```

A [custom type] stored as a constant cannot be modified via script, but _can_ be modified via a
registered Rust function that takes a first `&mut` parameter &ndash; because there is no way for
Rhai to know whether the Rust function modifies its argument!

By default, native Rust functions with a first `&mut` parameter always allow constants to be passed
to them. This is because using `&mut` can avoid unnecessary cloning of a [custom type] value, even
though it is actually not modified &ndash; for example returning the size of a collection type.

In line with intuition, Rhai is smart enough to always pass a _cloned copy_ of a constant as the
first `&mut` argument if the function is called in normal function call style.

If it is called as a [method], however, the Rust function will be able to modify the constant's value.

Also, property [setters][getters/setters] and [indexers] are always assumed to mutate the first
`&mut` parameter and so they always raise errors when passed constants by default.

```rust
// For the below, assume 'increment' is a Rust function with '&mut' first parameter

const X = 42;       // a constant

increment(X);       // call 'increment' in normal FUNCTION-CALL style
                    // since 'X' is constant, a COPY is passed instead

X == 42;            // value is 'X" is unchanged

X.increment();      // call 'increment' in METHOD-CALL style

X == 43;            // value of 'X' is changed!
                    // must use 'Dynamic::is_read_only' to check if parameter is constant

fn double() {
    this *= 2;      // function doubles 'this'
}

let y = 1;          // 'y' is not constant and mutable

y.double();         // double it...

y == 2;             // value of 'y' is changed as expected

X.double();         // since 'X' is constant, a COPY is passed to 'this'

X == 43;            // value of 'X' is unchanged by script
```

```admonish info.small "Implications on script optimization"

Rhai _assumes_ that constants are never changed, even via Rust functions.

This is important to keep in mind because the script [optimizer][script optimization]
by default does _constant propagation_ as a operation.

If a constant is eventually modified by a Rust function, the optimizer will not see
the updated value and will propagate the original initialization value instead.

`Dynamic::is_read_only` can be used to detect whether a [`Dynamic`] value is constant or not within
a Rust function.
```


# convert.md
Value Conversions
=================

{{#include ../links.md}}


Convert Between Integer and Floating-Point
------------------------------------------

| Function     | Not available under |                 From type                 |          To type          |
| ------------ | :-----------------: | :---------------------------------------: | :-----------------------: |
| `to_int`     |                     | `INT`, `FLOAT`, [`Decimal`][rust_decimal] |           `INT`           |
| `to_float`   |    [`no_float`]     | `INT`, `FLOAT`, [`Decimal`][rust_decimal] |          `FLOAT`          |
| `to_decimal` |   non-[`decimal`]   | `INT`, `FLOAT`, [`Decimal`][rust_decimal] | [`Decimal`][rust_decimal] |

That's it; for other conversions, register custom conversion functions.

```js
let x = 42;                     // 'x' is an integer

let y = x * 100.0;              // integer and floating-point can inter-operate

let y = x.to_float() * 100.0;   // convert integer to floating-point with 'to_float'

let z = y.to_int() + x;         // convert floating-point to integer with 'to_int'

let d = y.to_decimal();         // convert floating-point to Decimal with 'to_decimal'

let w = z.to_decimal() + x;     // Decimal and integer can inter-operate

let c = 'X';                    // character

print(`c is '${c}' and its code is ${c.to_int()}`); // prints "c is 'X' and its code is 88"
```


Parse String into Number
------------------------

| Function                                 | From type |          To type          |
| ---------------------------------------- | :-------: | :-----------------------: |
| `parse_int`                              | [string]  |           `INT`           |
| `parse_int` with radix 2-36              | [string]  |  `INT` (specified radix)  |
| `parse_float` (not [`no_float`])         | [string]  |          `FLOAT`          |
| `parse_float` ([`no_float`]+[`decimal`]) | [string]  | [`Decimal`][rust_decimal] |
| `parse_decimal` (requires [`decimal`])   | [string]  | [`Decimal`][rust_decimal] |

```rust
let x = parse_float("123.4");   // parse as floating-point
x == 123.4;
type_of(x) == "f64";

let x = parse_decimal("123.4"); // parse as Decimal value
type_of(x) == "decimal";

let x = 1234.to_decimal() / 10; // alternate method to create a Decimal value
type_of(x) == "decimal";

let dec = parse_int("42");      // parse as integer
dec == 42;
type_of(dec) == "i64";

let dec = parse_int("42", 10);  // radix = 10 is the default
dec == 42;
type_of(dec) == "i64";

let bin = parse_int("110", 2);  // parse as binary (radix = 2)
bin == 0b110;
type_of(bin) == "i64";

let hex = parse_int("ab", 16);  // parse as hex (radix = 16)
hex == 0xab;
type_of(hex) == "i64";
```


Format Numbers
--------------

| Function    | From type | To type  |             Format             |
| ----------- | :-------: | :------: | :----------------------------: |
| `to_binary` |   `INT`   | [string] | binary (i.e. only `1` and `0`) |
| `to_octal`  |   `INT`   | [string] |    octal (i.e. `0` ... `7`)    |
| `to_hex`    |   `INT`   | [string] |     hex (i.e. `0` ... `f`)     |

```rust
let x = 0x1234abcd;

x == 305441741;

x.to_string() == "305441741";

x.to_binary() == "10010001101001010101111001101";

x.to_octal() == "2215125715";

x.to_hex() == "1234abcd";
```


# do.md
Do Loop
=======

{{#include ../links.md}}

`do` loops have two opposite variants: `do` ... `while` and `do` ... `until`.

Like the [`while`] loop, `continue` can be used to skip to the next iteration, by-passing all
following statements; `break` can be used to break out of the loop unconditionally.

~~~admonish tip.small "Tip: Disable `do` loops"

`do` loops can be disabled via [`Engine::set_allow_looping`][options].
~~~

```rust
let x = 10;

do {
    x -= 1;
    if x < 6 { continue; }  // skip to the next iteration
    print(x);
    if x == 5 { break; }    // break out of do loop
} while x > 0;


do {
    x -= 1;
    if x < 6 { continue; }  // skip to the next iteration
    print(x);
    if x == 5 { break; }    // break out of do loop
} until x == 0;
```


Do Expression
-------------

Like Rust, `do` statements can also be used as _expressions_.

The `break` statement takes an optional expression that provides the return value.

The default return value of a `do` expression is [`()`].

~~~admonish tip.small "Tip: Disable all loop expressions"

Loop expressions can be disabled via [`Engine::set_allow_loop_expressions`][options].
~~~

```js
let x = 0;

// 'do' can be used just like an expression
let result = do {
    if is_magic_number(x) {
        // if the 'do' loop breaks here, return a specific value
        break get_magic_result(x);
    }

    x += 1;

    // ... if the 'do' loop exits here, the return value is ()
} until x >= 100;

if result == () {
    print("Magic number not found!");
} else {
    print(`Magic result = ${result}!`);
}
```


# doc-comments.md
Doc-Comments
============

{{#include ../links.md}}

Similar to Rust, [comments] starting with `///` (three slashes) or `/**` (two asterisks)
are _doc-comments_.

Doc-comments can only appear in front of [function] definitions, not any other elements.
Therefore, doc-comments are not available under [`no_function`].

~~~admonish warning.small "Requires `metadata`"

Doc-comments are only supported under the [`metadata`] feature.

If [`metadata`] is not active, doc-comments are treated as normal [comments].
~~~

```rust
/// This is a valid one-line doc-comment
fn foo() {}

/** This is a
 ** valid block
 ** doc-comment
 **/
fn bar(x) {
   /// Syntax error: this doc-comment is invalid
   x + 1
}

/** Syntax error: this doc-comment is invalid */
let x = 42;

/// Syntax error: this doc-comment is also invalid
{
   let x = 42;
}
```


~~~admonish tip "Tip: Special cases"

Long streams of `//////`... and `/*****`... do _NOT_ form doc-comments.
This is consistent with popular [comment] block styles for C-like languages.

```rust
///////////////////////////////  <- this is not a doc-comment
// This is not a doc-comment //  <- this is not a doc-comment
///////////////////////////////  <- this is not a doc-comment

// However, watch out for comment lines starting with '///'

//////////////////////////////////////////  <- this is not a doc-comment
/// This, however, IS a doc-comment!!! ///  <- doc-comment!
//////////////////////////////////////////  <- this is not a doc-comment

/****************************************
 *                                      *
 * This is also not a doc-comment block *
 * so we don't have to put this in      *
 * front of a function.                 *
 *                                      *
 ****************************************/
```
~~~


Using Doc-Comments
------------------

Doc-comments are stored within the script's [`AST`] after compilation.

The `AST::iter_functions` method provides a `ScriptFnMetadata` instance for each function defined
within the script, which includes doc-comments.

Doc-comments never affect the evaluation of a script nor do they incur significant performance overhead.
However, third party tools can take advantage of this information to auto-generate documentation for
Rhai script functions.


# dynamic-rust.md
Interop `Dynamic` Data with Rust
================================

{{#include ../links.md}}


Create a `Dynamic` from Rust Type
---------------------------------

| Rust type<br/>`T: Clone`,<br/>`K: Into<String>`                    |     Unavailable under     | Use API                      |
| ------------------------------------------------------------------ | :-----------------------: | ---------------------------- |
| `INT` (`i64` or `i32`)                                             |                           | `value.into()`               |
| `FLOAT` (`f64` or `f32`)                                           |       [`no_float`]        | `value.into()`               |
| [`Decimal`][rust_decimal] (requires [`decimal`])                   |                           | `value.into()`               |
| `bool`                                                             |                           | `value.into()`               |
| [`()`]                                                             |                           | `value.into()`               |
| [`String`][string], [`&str`][string], [`ImmutableString`]          |                           | `value.into()`               |
| `char`                                                             |                           | `value.into()`               |
| [`Array`][array]                                                   |       [`no_index`]        | `Dynamic::from_array(value)` |
| [`Blob`][BLOB]                                                     |       [`no_index`]        | `Dynamic::from_blob(value)`  |
| `Vec<T>`, `&[T]`, `Iterator<T>`                                    |       [`no_index`]        | `value.into()`               |
| [`Map`][object map]                                                |       [`no_object`]       | `Dynamic::from_map(value)`   |
| `HashMap<K, T>`, `HashSet<K>`,<br/>`BTreeMap<K, T>`, `BTreeSet<K>` |       [`no_object`]       | `value.into()`               |
| [`INT..INT`][range], [`INT..=INT`][range]                          |                           | `value.into()`               |
| `Rc<RwLock<T>>` or `Arc<Mutex<T>>`                                 |      [`no_closure`]       | `value.into()`               |
| [`Instant`][timestamp]                                             | [`no_time`] or [`no_std`] | `value.into()`               |
| All types (including above)                                        |                           | `Dynamic::from(value)`       |


Type Checking and Casting
-------------------------

~~~admonish tip.side "Tip: `try_cast` and `try_cast_result`"

The `try_cast` method does not panic but returns `None` upon failure.

The `try_cast_result` method also does not panic but returns the original value upon failure.
~~~

A [`Dynamic`] value's actual type can be checked via `Dynamic::is`.

The `cast` method then converts the value into a specific, known type.

Use `clone_cast` to clone a reference to [`Dynamic`].

```rust
let list: Array = engine.eval("...")?;      // return type is 'Array'
let item = list[0].clone();                 // an element in an 'Array' is 'Dynamic'

item.is::<i64>() == true;                   // 'is' returns whether a 'Dynamic' value is of a particular type

let value = item.cast::<i64>();             // if the element is 'i64', this succeeds; otherwise it panics
let value: i64 = item.cast();               // type can also be inferred

let value = item.try_cast::<i64>()?;        // 'try_cast' does not panic when the cast fails, but returns 'None'

let value = list[0].clone_cast::<i64>();    // use 'clone_cast' on '&Dynamic'
let value: i64 = list[0].clone_cast();
```


Type Name and Matching Types
----------------------------

The `type_name` method gets the name of the actual type as a static string slice,
which can be `match`-ed against.

This is a very simple and direct way to act on a [`Dynamic`] value based on the actual type of
the data value.

```rust
let list: Array = engine.eval("...")?;      // return type is 'Array'
let item = list[0];                         // an element in an 'Array' is 'Dynamic'

match item.type_name() {                    // 'type_name' returns the name of the actual Rust type
    "()" => ...
    "i64" => ...
    "f64" => ...
    "rust_decimal::Decimal" => ...
    "core::ops::range::Range<i64>" => ...
    "core::ops::range::RangeInclusive<i64>" => ...
    "alloc::string::String" => ...
    "bool" => ...
    "char" => ...
    "rhai::FnPtr" => ...
    "std::time::Instant" => ...
    "crate::path::to::module::TestStruct" => ...
        :
}
```

```admonish warning.small "Always full path name"

`type_name` always returns the _full_ Rust path name of the type, even when the type
has been registered with a friendly name via `Engine::register_type_with_name`.

This behavior is different from that of the [`type_of`][`type_of()`] function in Rhai.
```


Getting a Reference to Data
---------------------------

Use `Dynamic::read_lock` and `Dynamic::write_lock` to get an immutable/mutable reference to the data
inside a [`Dynamic`].

```rust
struct TheGreatQuestion {
    answer: i64
}

let question = TheGreatQuestion { answer: 42 };

let mut value: Dynamic = Dynamic::from(question);

let q_ref: &TheGreatQuestion =
        &*value.read_lock::<TheGreatQuestion>().unwrap();
//                       ^^^^^^^^^^^^^^^^^^^^ cast to data type

println!("answer = {}", q_ref.answer);          // prints 42

let q_mut: &mut TheGreatQuestion =
        &mut *value.write_lock::<TheGreatQuestion>().unwrap();
//                            ^^^^^^^^^^^^^^^^^^^^ cast to data type

q_mut.answer = 0;                               // mutate value

let value = value.cast::<TheGreatQuestion>();

println!("new answer = {}", value.answer);      // prints 0
```

~~~admonish question "TL;DR &ndash; Why `read_lock` and `write_lock`?"

As the naming shows, something is _locked_ in order to allow accessing the data within a [`Dynamic`],
and that something is a _shared value_ created by capturing variables from [closures].

Shared values are implemented as `Rc<RefCell<Dynamic>>` (`Arc<RwLock<Dynamic>>` under [`sync`]).

If the value is _not_ a shared value, or if running under [`no_closure`] where there is
no capturing, this API de-sugars to a simple reference cast.

In other words, there is no locking and reference counting overhead for the vast majority of
non-shared values.

If the value _is_ a shared value, then it is first _locked_ and the returned _lock guard_
allows access to the underlying value in the specified type.
~~~


Methods and Traits
------------------

The following methods are available when working with [`Dynamic`]:

| Method          |     Not available under     |        Return type        | Description                                                                                                                                         |
| --------------- | :-------------------------: | :-----------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type_name`     |                             |          `&str`           | name of the value's type                                                                                                                            |
| `into_shared`   |       [`no_closure`]        |        [`Dynamic`]        | turn the value into a _shared_ value                                                                                                                |
| `flatten_clone` |                             |        [`Dynamic`]        | clone the value (a _shared_ value, if any, is cloned into a separate copy)                                                                          |
| `flatten`       |                             |        [`Dynamic`]        | clone the value into a separate copy if it is _shared_ and there are multiple outstanding references, otherwise _shared_ values are turned unshared |
| `read_lock<T>`  | [`no_closure`] (pass thru') | `Option<` _guard to_ `T>` | lock the value for reading                                                                                                                          |
| `write_lock<T>` | [`no_closure`] (pass thru') | `Option<` _guard to_ `T>` | lock the value exclusively for writing                                                                                                              |
| `deep_scan`     |                             |                           | recursively scan for [`Dynamic`] values (e.g. items inside an [array] or [object map], or [curried arguments][currying] in a [function pointer])    |

### Constructor instance methods

| Method           |    Not available under    |                         Value type                          |         Data type         |
| ---------------- | :-----------------------: | :---------------------------------------------------------: | :-----------------------: |
| `from_bool`      |                           |                           `bool`                            |          `bool`           |
| `from_int`       |                           |                            `INT`                            |      integer number       |
| `from_float`     |       [`no_float`]        |                           `FLOAT`                           |   floating-point number   |
| `from_decimal`   |      non-[`decimal`]      |                  [`Decimal`][rust_decimal]                  | [`Decimal`][rust_decimal] |
| `from_str`       |                           |                           `&str`                            |         [string]          |
| `from_char`      |                           |                           `char`                            |        [character]        |
| `from_array`     |       [`no_index`]        |                          `Vec<T>`                           |          [array]          |
| `from_blob`      |       [`no_index`]        |                          `Vec<u8>`                          |          [BLOB]           |
| `from_map`       |       [`no_object`]       |                            `Map`                            |       [object map]        |
| `from_timestamp` | [`no_time`] or [`no_std`] | `std::time::Instant` ([`instant::Instant`] if [WASM] build) |        [timestamp]        |
| `from<T>`        |                           |                             `T`                             |       [custom type]       |

### Detection methods

| Method         |    Not available under    | Return type | Description                                                            |
| -------------- | :-----------------------: | :---------: | ---------------------------------------------------------------------- |
| `is<T>`        |                           |   `bool`    | is the value of type `T`?                                              |
| `is_variant`   |                           |   `bool`    | is the value a trait object (i.e. not one of Rhai's [standard types])? |
| `is_read_only` |                           |   `bool`    | is the value [constant]? A [constant] value should not be modified.    |
| `is_shared`    |      [`no_closure`]       |   `bool`    | is the value _shared_ via a [closure]?                                 |
| `is_locked`    |      [`no_closure`]       |   `bool`    | is the value _shared_ and locked (i.e. currently being read)?          |
| `is_unit`      |                           |   `bool`    | is the value [`()`]?                                                   |
| `is_int`       |                           |   `bool`    | is the value an integer?                                               |
| `is_float`     |       [`no_float`]        |   `bool`    | is the value a floating-point number?                                  |
| `is_decimal`   |      non-[`decimal`]      |   `bool`    | is the value a [`Decimal`][rust_decimal]?                              |
| `is_bool`      |                           |   `bool`    | is the value a `bool`?                                                 |
| `is_char`      |                           |   `bool`    | is the value a [character]?                                            |
| `is_string`    |                           |   `bool`    | is the value a [string]?                                               |
| `is_array`     |       [`no_index`]        |   `bool`    | is the value an [array]?                                               |
| `is_blob`      |       [`no_index`]        |   `bool`    | is the value a [BLOB]?                                                 |
| `is_map`       |       [`no_object`]       |   `bool`    | is the value an [object map]?                                          |
| `is_timestamp` | [`no_time`] or [`no_std`] |   `bool`    | is the value a [timestamp]?                                            |


### Casting methods

The following methods cast a [`Dynamic`] into a specific type:

| Method                    | Not available under |            Return type (error is name of actual type if `&str`)            |
| ------------------------- | :-----------------: | :------------------------------------------------------------------------: |
| `cast<T>`                 |                     |                          `T` (panics on failure)                           |
| `try_cast<T>`             |                     |                                `Option<T>`                                 |
| `try_cast_result<T>`      |                     |                            `Result<T, Dynamic>`                            |
| `clone_cast<T>`           |                     |                   cloned copy of `T` (panics on failure)                   |
| `as_unit`                 |                     |                             `Result<(), &str>`                             |
| `as_int`                  |                     |                            `Result<INT, &str>`                             |
| `as_float`                |    [`no_float`]     |                           `Result<FLOAT, &str>`                            |
| `as_decimal`              |   non-[`decimal`]   |                  [`Result<Decimal, &str>`][rust_decimal]                   |
| `as_bool`                 |                     |                            `Result<bool, &str>`                            |
| `as_char`                 |                     |                            `Result<char, &str>`                            |
| `as_immutable_string_ref` |                     |  [`Result<impl Deref<Target=ImmutableString>, &str>`][`ImmutableString`]   |
| `as_immutable_string_mut` |                     | [`Result<impl DerefMut<Target=ImmutableString>, &str>`][`ImmutableString`] |
| `as_array_ref`            |    [`no_index`]     |             [`Result<impl Deref<Target=Array>, &str>`][array]              |
| `as_array_mut`            |    [`no_index`]     |            [`Result<impl DerefMut<Target=Array>, &str>`][array]            |
| `as_blob_ref`             |    [`no_index`]     |              [`Result<impl Deref<Target=Blob>, &str>`][BLOB]               |
| `as_blob_mut`             |    [`no_index`]     |             [`Result<impl DerefMut<Target=Blob>, &str>`][BLOB]             |
| `as_map_ref`              |    [`no_object`]    |            [`Result<impl Deref<Target=Map>, &str>`][object map]            |
| `as_map_mut`              |    [`no_object`]    |          [`Result<impl DerefMut<Target=Map>, &str>`][object map]           |
| `into_string`             |                     |                           `Result<String, &str>`                           |
| `into_immutable_string`   |                     |            [`Result<ImmutableString, &str>`][`ImmutableString`]            |
| `into_array`              |    [`no_index`]     |                       [`Result<Array, &str>`][array]                       |
| `into_blob`               |    [`no_index`]     |                        [`Result<Blob, &str>`][BLOB]                        |
| `into_typed_array<T>`     |    [`no_index`]     |                           `Result<Vec<T>, &str>`                           |

### Constructor traits

The following constructor traits are implemented for [`Dynamic`] where `T: Clone`:

| Trait                                                                          |      Not available under       |         Data type         |
| ------------------------------------------------------------------------------ | :----------------------------: | :-----------------------: |
| `From<()>`                                                                     |                                |           `()`            |
| `From<INT>`                                                                    |                                |      integer number       |
| `From<FLOAT>`                                                                  |          [`no_float`]          |   floating-point number   |
| `From<Decimal>`                                                                |        non-[`decimal`]         | [`Decimal`][rust_decimal] |
| `From<bool>`                                                                   |                                |          `bool`           |
| `From<S: Into<ImmutableString>>`<br/>e.g. `From<String>`, `From<&str>`         |                                |    [`ImmutableString`]    |
| `From<char>`                                                                   |                                |        [character]        |
| `From<Vec<T>>`                                                                 |          [`no_index`]          |          [array]          |
| `From<&[T]>`                                                                   |          [`no_index`]          |          [array]          |
| `From<BTreeMap<K: Into<SmartString>, T>>`<br/>e.g. `From<BTreeMap<String, T>>` |         [`no_object`]          |       [object map]        |
| `From<BTreeSet<K: Into<SmartString>>>`<br/>e.g. `From<BTreeSet<String>>`       |         [`no_object`]          |       [object map]        |
| `From<HashMap<K: Into<SmartString>, T>>`<br/>e.g. `From<HashMap<String, T>>`   |  [`no_object`] or [`no_std`]   |       [object map]        |
| `From<HashSet<K: Into<SmartString>>>`<br/>e.g. `From<HashSet<String>>`         |  [`no_object`] or [`no_std`]   |       [object map]        |
| `From<FnPtr>`                                                                  |                                |    [function pointer]     |
| `From<Instant>`                                                                |   [`no_time`] or [`no_std`]    |        [timestamp]        |
| `From<Rc<RefCell<Dynamic>>>`                                                   |   [`sync`] or [`no_closure`]   |        [`Dynamic`]        |
| `From<Arc<RwLock<Dynamic>>>` ([`sync`])                                        | non-[`sync`] or [`no_closure`] |        [`Dynamic`]        |
| `FromIterator<X: IntoIterator<Item=T>>`                                        |          [`no_index`]          |          [array]          |


# dynamic-tag.md
Dynamic Value Tag
=================

{{#include ../links.md}}

Each [`Dynamic`] value can contain a _tag_ that is `i32` and can contain any arbitrary data.

On 32-bit targets, however, the tag is only `i16`.

The tag defaults to zero.

```admonish bug.small "Value out of bounds"

It is an error to set a tag to a value beyond the bounds of `i32` (`i16` on 32-bit targets).
```


Examples
--------

```rust
let x = 42;

x.tag == 0;             // tag defaults to zero

x.tag = 123;            // set tag value

set_tag(x, 123);        // 'set_tag' function also works

x.tag == 123;           // get updated tag value

x.tag() == 123;         // method also works

tag(x) == 123;          // function call style also works

x.tag[3..5] = 2;        // tag can be used as a bit-field

x.tag[3..5] == 2;

let y = x;

y.tag == 123;           // the tag is copied across assignment

y.tag = 3000000000;     // runtime error: 3000000000 is too large for 'i32'
```


Practical Applications
----------------------

Attaching arbitrary information together with a value has a lot of practical uses.

### Identify code path

For example, it is easy to attach an ID number to a value to indicate how or why that value is
originally set.

This is tremendously convenient for debugging purposes where it is necessary to figure out which
code path a particular value went through.

After the script is verified, all tag assignment statements can simply be removed.

```js
const ROUTE1 = 1;
const ROUTE2 = 2;
const ROUTE3 = 3;
const ERROR_ROUTE = 9;

fn some_complex_calculation(x) {
    let result;

    if some_complex_condition(x) {
        result = 42;
        result.tag = ROUTE1;        // record route #1
    } else if some_other_very_complex_condition(x) == 1 {
        result = 123;
        result.tag = ROUTE2;        // record route #2
    } else if some_non_understandable_calculation(x) > 0 {
        result = 0;
        result.tag = ROUTE3;        // record route #3
    } else {
        result = -1;
        result.tag = ERROR_ROUTE;   // record error
    }

    result  // this value now contains the tag
}

let my_result = some_complex_calculation(key);

// The code path that 'my_result' went through is now in its tag.

// It is now easy to trace how 'my_result' gets its final value.

print(`Result = ${my_result} and reason = ${my_result.tag}`);
```

### Identify data source

It is convenient to use the tag value to record the _source_ of a piece of data.

```js
let x = [0, 1, 2, 3, 42, 99, 123];

// Store the index number of each value into its tag before
// filtering out all even numbers, leaving only odd numbers
let filtered = x.map(|v, i| { v.tag = i; v }).filter(|v| v.is_odd());

// The tag now contains the original index position

for (data, i) in filtered {
    print(`${i + 1}: Value ${data} from position #${data.tag + 1}`);
}
```

### Identify code conditions

The tag value may also contain a _[bit-field]_ of up to 32 (16 under 32-bit targets) individual bits,
recording up to 32 (or 16 under 32-bit targets) logic conditions that contributed to the value.

Again, after the script is verified, all tag assignment statements can simply be removed.

```js

fn some_complex_calculation(x) {
    let result = x;

    // Check first condition
    if some_complex_condition() {
        result += 1;
        result.tag[0] = true;   // Set first bit in bit-field
    }

    // Check second condition
    if some_other_very_complex_condition(x) == 1 {
        result *= 10;
        result.tag[1] = true;   // Set second bit in bit-field
    }

    // Check third condition
    if some_non_understandable_calculation(x) > 0 {
        result -= 42;
        result.tag[2] = true;   // Set third bit in bit-field
    }

    // Check result
    if result > 100 {
        result = 0;
        result.tag[3] = true;   // Set forth bit in bit-field
    }

    result
}

let my_result = some_complex_calculation(42);

// The tag of 'my_result' now contains a bit-field indicating
// the result of each condition.

// It is now easy to trace how 'my_result' gets its final value.
// Use indexing on the tag to get at individual bits.

print(`Result = ${my_result}`);
print(`First condition = ${my_result.tag[0]}`);
print(`Second condition = ${my_result.tag[1]}`);
print(`Third condition = ${my_result.tag[2]}`);
print(`Result check = ${my_result.tag[3]}`);
```

### Return auxillary info

Sometimes it is useful to return auxillary info from a [function].

```rust
// Verify Bell's Inequality by calculating a norm
// and comparing it with a hypotenuse.
// https://en.wikipedia.org/wiki/Bell%27s_theorem
//
// Returns the smaller of the norm or hypotenuse.
// Tag is 1 if norm <= hypo, 0 if otherwise.
fn bells_inequality(x, y, z) {
    let norm = sqrt(x ** 2 + y ** 2);
    let result;

    if norm <= z {
        result = norm;
        result.tag = 1;
    } else {
        result = z;
        result.tag = 0;
    }

    result
}

let dist = bells_inequality(x, y, z);

print(`Value = ${dist}`);

if dist.tag == 1 {
    print("Local realism maintained! Einstein rules!");
} else {
    print("Spooky action at a distance detected! Einstein will hate this...");
}
```

### Poor-man's tuples

Rust has _tuples_ but Rhai does not (nor does JavaScript in this sense).

Similar to the JavaScript situation, practical alternatives using Rhai include returning an
[object map] or an [array].

Both of these alternatives, however, incur overhead that may be wasteful when the amount of
additional information is small &ndash; e.g. in many cases, a single `bool`, or a small number.

To return a number of _small_ values from [functions], the tag value as a [bit-field] is an ideal
container without resorting to a full-blown [object map] or [array].

```rust
// This function essentially returns a tuple of four numbers:
// (result, a, b, c)
fn complex_calc(x, y, z) {
    let a = x + y;
    let b = x - y + z;
    let c = (a + b) * z / y;
    let r = do_complex_calculation(a, b, c);

    // Store 'a', 'b' and 'c' into tag if they are small
    r.tag[0..8] = a;
    r.tag[8..16] = b;
    r.tag[16..32] = c;

    r
}

// Deconstruct the tuple
let result = complex_calc(x, y, z);
let a = r.tag[0..8];
let b = r.tag[8..16];
let c = r.tag[16..32];
```


TL;DR
-----

```admonish question "Tell me, really, what is the _point_?"

Due to byte alignment requirements on modern CPU's, there are unused spaces in a [`Dynamic`] type,
of the order of 4 bytes on 64-bit targets (2 bytes on 32-bit).

It is empty space that can be put to good use and not wasted, especially when Rhai does not have
built-in support of tuples in order to return multiple values from [functions].
```


# dynamic.md
Dynamic Values
==============

{{#include ../links.md}}

A `Dynamic` value can be _any_ type, as long as it implements `Clone`.

~~~admonish warning.small "`Send + Sync`"

Under the [`sync`] feature, all types must also be `Send + Sync`.
~~~

```rust
let x = 42;         // value is an integer

x = 123.456;        // value is now a floating-point number

x = "hello";        // value is now a string

x = x.len > 0;      // value is now a boolean

x = [x];            // value is now an array

x = #{x: x};        // value is now an object map
```


Use `type_of()` to Get Value Type
---------------------------------

Because [`type_of()`] a `Dynamic` value returns the type of the actual value,
it is usually used to perform type-specific actions based on the actual value's type.

```js
let mystery = get_some_dynamic_value();

switch type_of(mystery) {
    "()" => print("Hey, I got the unit () here!"),
    "i64" => print("Hey, I got an integer here!"),
    "f64" => print("Hey, I got a float here!"),
    "decimal" => print("Hey, I got a decimal here!"),
    "range" => print("Hey, I got an exclusive range here!"),
    "range=" => print("Hey, I got an inclusive range here!"),
    "string" => print("Hey, I got a string here!"),
    "bool" => print("Hey, I got a boolean here!"),
    "array" => print("Hey, I got an array here!"),
    "blob" => print("Hey, I got a BLOB here!"),
    "map" => print("Hey, I got an object map here!"),
    "Fn" => print("Hey, I got a function pointer here!"),
    "timestamp" => print("Hey, I got a time-stamp here!"),
    "TestStruct" => print("Hey, I got the TestStruct custom type here!"),
    _ => print(`I don't know what this is: ${type_of(mystery)}`)
}
```


Parse from JSON
---------------

~~~admonish warning.side "Requires `metadata`"

`parse_json` is defined in the [`LanguageCorePackage`][built-in packages], which is excluded when using a [raw `Engine`].

It also requires the [`metadata`] feature; the [`no_index`] and [`no_object`] features must _not_ be set.
~~~

Use `parse_json` to parse a JSON string into a [`Dynamic`] value.

|           JSON type           |  Rhai type   |
| :---------------------------: | :----------: |
|  `number` (no decimal point)  |    `INT`     |
| `number` (with decimal point) |   `FLOAT`    |
|           `string`            |   [string]   |
|           `boolean`           |    `bool`    |
|            `Array`            |   [array]    |
|           `Object`            | [object map] |
|            `null`             |    [`()`]    |


# eval.md
`eval` Function
===============

{{#include ../links.md}}

Or "How to Shoot Yourself in the Foot even Easier"
--------------------------------------------------

Saving the best for last, there is the ever-dreaded... `eval` [function]!

```rust
let x = 10;

fn foo(x) { x += 12; x }

let script =
"
    let y = x;
    y += foo(y);
    x + y
";

let result = eval(script);      // <- look, JavaScript, we can also do this!

result == 42;

x == 10;                        // prints 10 - arguments are passed by value
y == 32;                        // prints 32 - variables defined in 'eval' persist!

eval("{ let z = y }");          // to keep a variable local, use a statements block

print(z);                       // <- error: variable 'z' not found

"print(42)".eval();             // <- nope... method-call style doesn't work with 'eval'
```

~~~admonish danger.small "`eval` executes inside the current scope!"

Script segments passed to `eval` execute inside the _current_ [`Scope`], so they can access and modify
_everything_, including all [variables] that are visible at that position in code!

```rust
let script = "x += 32";

let x = 10;
eval(script);       // variable 'x' is visible!
print(x);           // prints 42

// The above is equivalent to:
let script = "x += 32";
let x = 10;
x += 32;
print(x);
```

`eval` can also be used to define new [variables] and do other things normally forbidden inside
a [function] call.

```rust
let script = "let x = 42";
eval(script);
print(x);           // prints 42
```

Treat it as if the script segments are physically pasted in at the position of the `eval` call.
~~~

~~~admonish warning.small "Cannot define new functions"

New [functions] cannot be defined within an `eval` call, since [functions] can only be defined at
the _global_ level!
~~~

~~~admonish failure.small "`eval` is evil"

For those who subscribe to the (very sensible) motto of ["`eval` is evil"](https://www.oreilly.com/library/view/javascript-the-good/9780596517748/apcs21.html),
disable `eval` via [`Engine::disable_symbol`][disable keywords and operators].

```rust
// Disable usage of 'eval'
engine.disable_symbol("eval");
```
~~~


~~~admonish question.small "Do you regret implementing `eval` in Rhai?"

Or course we do.

Having the possibility of an `eval` call disrupts any predictability in the Rhai script,
thus disabling a large number of optimizations.
~~~

```admonish question.small "Why did it then???!!!"

Brendan Eich puts it well: "it is just too easy to implement." _(source wanted)_
```


# float-comp.md
Floating-point Comparison
=========================

{{#include ../links.md}}


0.1 + 0.2 ≠ 0.3
---------------

```admonish info.side.wide "See Also"

See also [_this article_](https://randomascii.wordpress.com/2012/02/25/comparing-floating-point-numbers-2012-edition/)
for a detailed discussion on comparing floating-point numbers.
```

Comparing floating-point numbers are tricky because they often fail miserably and unexpectedly.

Take the infamous `0.1 + 0.2 ≠ 0.3` example from most languages:

```js
// JavaScript example

let x = 0.3;            // 0.3
let y = 0.1 + 0.2;      // 0.3?

console.log(x == y);    // false!

console.log(x);         // 0.3
console.log(y);         // 0.30000000000000004
```


Epsilon-Based Implementation
----------------------------

```admonish warning.small "Warning"

If the [`unchecked`] feature is enabled, then all floating-point comparisons are done as per IEEE 754 standard.
```

The IEEE 754 standard for floating-point arithmetic provides an
[_epsilon_](https://en.wikipedia.org/wiki/Machine_epsilon) value that can be used to compare floating-point numbers.

With `max_diff = max(|x|, |y|) × epsilon`, Rhai compares floating-point numbers based on the following:

| operator |   operands    | algorithm                   |
| :------: | :-----------: | --------------------------- |
| `x == y` |   has zero    | `\|x - y\|` < _epsilon_     |
| `x == y` | both non-zero | `\|x - y\|` < _epsilon_     |
| `x != y` |   has zero    | `\|x - y\|` ≥ _epsilon_     |
| `x != y` | both non-zero | `\|x - y\|` ≥ `max_diff`    |
| `x > y`  |   has zero    | `x - y` ≥ _epsilon_         |
| `x > y`  | both non-zero | `x - y` ≥ `max_diff`        |
| `x >= y` |   has zero    | `x - y` ≥ &ndash;_epsilon_  |
| `x >= y` | both non-zero | `x - y` ≥ &ndash;`max_diff` |
| `x < y`  |   has zero    | `y - x` ≥ _epsilon_         |
| `x < y`  | both non-zero | `y - x` ≥ `max_diff`        |
| `x <= y` |   has zero    | `y - x` ≥ &ndash;_epsilon_  |
| `x <= y` | both non-zero | `y - x` ≥ &ndash;`max_diff` |


Casual Scripting Usage
----------------------

For most scripts that casually compare floating-point numbers, the default behavior is sufficient to
cover all bases:

```rust
let x = 0.3;            // 0.3
let y = 0.1 + 0.2;      // 0.3?

x == y == true;         // 0.1 + 0.2 = 0.3. Just Works!

let x = 1e-16;          // 0.0000000000000001
x > 0 == false;         // comparing with zero Just Works when value is very small
x == 0 == true;

let x = 1e-15;          // 0.000000000000001
x > 0 == true;          // comparing with zero when value above epsilon
x == 0 == false;

let x = 1e-28;          // 0.0000000000000000000000000001
let y = 1e-29;          // 0.00000000000000000000000000001, 10x smaller than 'x'
x > y == true;          // comparing very small numbers actually wide apart!

let x = 0.00000000000000000001;
let y = 0.000000000000000000010000000000000001;
x < y == false;         // difference is small enough for 'x' == 'y'

let y = 0.00000000000000000001000000000000001;
x < y = true;           // difference is not small enough for 'x' == 'y'
```


# fn-anon.md
Anonymous Functions
===================

{{#include ../links.md}}

Many functions in the standard API expect [function pointer] as parameters.

For example:

```rust
// Function 'double' defined here - used only once
fn double(x) { 2 * x }

// Function 'square' defined here - again used only once
fn square(x) { x * x }

let x = [1, 2, 3, 4, 5];

// Pass a function pointer to 'double'
let y = x.map(double);

// Pass a function pointer to 'square' using Fn(...) notation
let z = y.map(Fn("square"));
```

Sometimes it gets tedious to define separate [functions] only to dispatch them via single [function pointers] &ndash;
essentially, those [functions] are only ever called in one place.

This scenario is especially common when simulating object-oriented programming ([OOP]).

```rust
// Define functions one-by-one
fn obj_inc(x, y) { this.data += x * y; }
fn obj_dec(x) { this.data -= x; }
fn obj_print() { print(this.data); }

// Define object
let obj = #{
    data: 42,
    increment: obj_inc,     // use function pointers to
    decrement: obj_dec,     // refer to method functions
    print: obj_print
};
```


Syntax
------

Anonymous [functions] have a syntax similar to Rust's _closures_ (they are _not_ the same).

> `|`_param 1_`,` _param 2_`,` ... `,` _param n_`|` _statement_  
>
> `|`_param 1_`,` _param 2_`,` ... `,` _param n_`| {` _statements_... `}`  

No parameters:

> `||` _statement_  
>
> `|| {` _statements_... `}`

Anonymous functions can be disabled via [`Engine::set_allow_anonymous_function`][options].


Rewrite Using Anonymous Functions
---------------------------------

The above can be rewritten using _anonymous [functions]_.

```rust
let x = [1, 2, 3, 4, 5];

let y = x.map(|x| 2 * x);

let z = y.map(|x| x * x);

let obj = #{
    data: 42,
    increment: |x, y| this.data += x * y,   // one statement
    decrement: |x| this.data -= x,          // one statement
    print_obj: || {
        print(this.data);                   // full function body
    }
};
```

This de-sugars to:

```rust
// Automatically generated...
fn anon_fn_0001(x) { 2 * x }
fn anon_fn_0002(x) { x * x }
fn anon_fn_0003(x, y) { this.data += x * y; }
fn anon_fn_0004(x) { this.data -= x; }
fn anon_fn_0005() { print(this.data); }

let x = [1, 2, 3, 4, 5];

let y = x.map(anon_fn_0001);

let z = y.map(anon_fn_0002);

let obj = #{
    data: 42,
    increment: anon_fn_0003,
    decrement: anon_fn_0004,
    print: anon_fn_0005
};
```


# fn-closure.md
Closures
========

{{#include ../links.md}}

~~~admonish tip.side "Tip: `is_shared`"

Use `Dynamic::is_shared` to check whether a particular [`Dynamic`] value is shared.
~~~

Although [anonymous functions] de-sugar to standard function definitions, they differ from standard
functions because they can _captures_ [variables] that are not defined within the current scope,
but are instead defined in an external scope &ndash; i.e. where the [anonymous function] is created.

All [variables] that are accessible during the time the [anonymous function] is created are
automatically captured when they are used, as long as they are not shadowed by local [variables]
defined within the function's.

The captured [variables] are automatically converted into **reference-counted shared values**
(`Rc<RefCell<Dynamic>>`, or `Arc<RwLock<Dynamic>>` under [`sync`]).

Therefore, similar to closures in many languages, these captured shared values persist through
reference counting, and may be read or modified even after the [variables] that hold them go out of
scope and no longer exist.

```admonish tip.small "Tip: Disable closures"

Capturing external [variables] can be turned off via the [`no_closure`] feature.
```


Examples
--------

```rust
let x = 1;                          // a normal variable

x.is_shared() == false;

let f = |y| x + y;                  // variable 'x' is auto-curried (captured) into 'f'

x.is_shared() == true;              // 'x' is now a shared value!

f.call(2) == 3;                     // 1 + 2 == 3

x = 40;                             // changing 'x'...

f.call(2) == 42;                    // the value of 'x' is 40 because 'x' is shared

// The above de-sugars into something like this:

fn anon_0001(x, y) { x + y }        // parameter 'x' is inserted

make_shared(x);                     // convert variable 'x' into a shared value

let f = anon_0001.curry(x);         // shared 'x' is curried
```


~~~admonish bug "Beware: Captured Variables are Truly Shared"

The example below is a typical tutorial sample for many languages to illustrate the traps
that may accompany capturing external [variables] in closures.

It prints `9`, `9`, `9`, ... `9`, `9`, not `0`, `1`, `2`, ... `8`, `9`, because there is
ever only _one_ captured [variable], and all ten closures capture the _same_ [variable].

```rust
let list = [];

for i in 0..10 {
    list.push(|| print(i));         // the for loop variable 'i' is captured
}

list.len() == 10;                   // 10 closures stored in the array

list[0].type_of() == "Fn";          // make sure these are closures

for f in list {
    f.call();                       // all references to 'i' are the same variable!
}
```
~~~

~~~admonish danger "Be Careful to Prevent Data Races"

Rust does not have data races, but that doesn't mean Rhai doesn't.

Avoid performing a method call on a captured shared [variable] (which essentially takes a
mutable reference to the shared object) while using that same [variable] as a parameter
in the method call &ndash; this is a sure-fire way to generate a data race error.

If a shared value is used as the `this` pointer in a method call to a closure function,
then the same shared value _must not_ be captured inside that function, or a data race
will occur and the script will terminate with an error.

```rust
let x = 20;

x.is_shared() == false;             // 'x' is not shared, so no data race is possible

let f = |a| this += x + a;          // 'x' is captured in this closure

x.is_shared() == true;              // now 'x' is shared

x.call(f, 2);                       // <- error: data race detected on 'x'
```
~~~

~~~admonish danger "Data Races in `sync` Builds Can Become Deadlocks"

Under the [`sync`] feature, shared values are guarded with a `RwLock`, meaning that data race
conditions no longer raise an error.

Instead, they wait endlessly for the `RwLock` to be freed, and thus can become deadlocks.

On the other hand, since the same thread (i.e. the [`Engine`] thread) that is holding the lock
is attempting to read it again, this may also [panic](https://doc.rust-lang.org/std/sync/struct.RwLock.html#panics-1)
depending on the O/S.

```rust
let x = 20;

let f = |a| this += x + a;          // 'x' is captured in this closure

// Under `sync`, the following may wait forever, or may panic,
// because 'x' is locked as the `this` pointer but also accessed
// via a captured shared value.
x.call(f, 2);
```
~~~


TL;DR
-----

```admonish question "How is it actually implemented?"

The actual implementation of closures de-sugars to:

1. Keeping track of what [variables] are accessed inside the [anonymous function],

2. If a [variable] is not defined within the [anonymous function's][anonymous function] scope,
   it is looked up _outside_ the [function] and in the current execution scope &ndash;
   where the [anonymous function] is created.

3. The [variable] is added to the parameters list of the [anonymous function], at the front.

4. The [variable] is then converted into a **reference-counted shared value**.

   An [anonymous function] which captures an external [variable] is the only way to create a
   reference-counted shared value in Rhai.

5. The shared value is then [curried][currying] into the [function pointer] itself,
   essentially carrying a reference to that shared value and inserting it into future calls of the [function].

   This process is called _Automatic Currying_, and is the mechanism through which Rhai simulates closures.
```

```admonish question "Why automatic currying?"

In concept, a closure _closes_ over captured variables from the outer scope &ndash; that's why
they are called _closures_.  When this happen, a typical language implementation hoists
those variables that are captured away from the stack frame and into heap-allocated storage.
This is because those variables may be needed after the stack frame goes away.

These heap-allocated captured variables only go away when all the closures that need them
are finished with them.  A garbage collector makes this trivial to implement &ndash; they are
automatically collected as soon as all closures needing them are destroyed.

In Rust, this can be done by reference counting instead, with the potential pitfall of creating
reference loops that will prevent those variables from being deallocated forever.
Rhai avoids this by clone-copying most data values, so reference loops are hard to create.

Rhai does the hoisting of captured variables into the heap by converting those values
into reference-counted locked values, also allocated on the heap.  The process is identical.

Closures are usually implemented as a data structure containing two items:

1. A function pointer to the function body of the closure,
2. A data structure containing references to the captured shared variables on the heap.

Usually a language implementation passes the structure containing references to captured
shared variables into the function pointer, the function body taking this data structure
as an additional parameter.

This is essentially what Rhai does, except that Rhai passes each variable individually
as separate parameters to the function, instead of creating a structure and passing that
structure as a single parameter.  This is the only difference.

Therefore, in most languages, essentially all closures are implemented as automatic currying of
shared variables hoisted into the heap, automatically passing those variables as parameters into
the function. Rhai just brings this directly up to the front.
```


# fn-curry.md
Function Pointer Currying
=========================

{{#include ../links.md}}

It is possible to _curry_ a [function pointer] by providing partial (or all) arguments.

Currying is done via the `curry` keyword and produces a new [function pointer] which carries
the curried arguments.

When the curried [function pointer] is called, the curried arguments are inserted starting from the _left_.

The actual call arguments should be reduced by the number of curried arguments.

```rust
fn mul(x, y) {                  // function with two parameters
    x * y
}

let func = mul;                 // <- de-sugars to 'Fn("mul")'

func.call(21, 2) == 42;         // two arguments are required for 'mul'

let curried = func.curry(21);   // currying produces a new function pointer which
                                // carries 21 as the first argument

let curried = curry(func, 21);  // function-call style also works

curried.call(2) == 42;          // <- de-sugars to 'func.call(21, 2)'
                                //    only one argument is now required
```


# fn-metadata.md
Get Functions Metadata in Scripts
=================================

{{#include ../links.md}}

The built-in function `get_fn_metadata_list` returns an [array] of [object maps], each containing
the metadata of one script-defined [function] in scope.

`get_fn_metadata_list` is defined in the [`LanguageCorePackage`][built-in packages], which is
excluded when using a [raw `Engine`].

`get_fn_metadata_list` has a few versions taking different parameters:

| Signature                            | Description                                                                                                                             |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `get_fn_metadata_list()`             | returns an [array] for _all_ script-defined [functions]                                                                                 |
| `get_fn_metadata_list(name)`         | returns an [array] containing all script-defined [functions] matching a specified name                                                  |
| `get_fn_metadata_list(name, params)` | returns an [array] containing all script-defined [functions] matching a specified name and accepting the specified number of parameters |

[Functions] from the following sources are returned, in order:

1. Encapsulated script environment (e.g. when loading a [module] from a script file),
2. Current script,
3. [Modules] registered via `Engine::register_global_module` (latest registrations first)
4. [Modules] imported via the [`import`] statement (latest imports first),
5. [Modules] added via `Engine::register_static_module` (latest registrations first)

The return value is an [array] of [object maps] (so `get_fn_metadata_list` is also not available under
[`no_index`] or [`no_object`]), containing the following fields.

| Field          |            Type            | Optional? | Description                                                                         |
| -------------- | :------------------------: | :-------: | ----------------------------------------------------------------------------------- |
| `namespace`    |          [string]          |  **yes**  | the module _namespace_ if the [function] is defined within a [module]               |
| `access`       |          [string]          |    no     | `"public"` if the function is public,<br/>`"private"` if it is [private][`private`] |
| `name`         |          [string]          |    no     | [function] name                                                                     |
| `params`       |    [array] of [strings]    |    no     | parameter names                                                                     |
| `this_type`    | [string](strings-chars.md) |  **yes**  | restrict the type of `this` if the [function] is a [method]                         |
| `is_anonymous` |           `bool`           |    no     | is this [function] an [anonymous function]?                                         |
| `comments`     |    [array] of [strings]    |  **yes**  | [doc-comments], if any, one per line                                                |


# fn-method.md
`this` &ndash; Simulating an Object Method
==========================================

{{#include ../links.md}}

```admonish warning.side "Functions are pure"

The only way for a script-defined [function] to change an external value is via `this`.
```

Arguments passed to script-defined [functions] are always by _value_ because [functions] are _pure_.

However, [functions] can also be called in _method-call_ style (not available under [`no_object`]):

> _object_ `.` _method_ `(` _parameters_ ... `)`

When a [function] is called this way, the keyword `this` binds to the object in the method call and
can be changed.

```rust
fn change() {       // note that the method does not need a parameter
    this = 42;      // 'this' binds to the object in method-call
}

let x = 500;

x.change();         // call 'change' in method-call style, 'this' binds to 'x'

x == 42;            // 'x' is changed!

change();           // <- error: 'this' is unbound
```


Elvis Operator
--------------

The [_Elvis_ operator][elvis] can be used to short-circuit the method call when the object itself is [`()`].

> _object_ `?.` _method_ `(` _parameters_ ... `)`

In the above, the _method_ is never called if _object_ is [`()`].


Restrict the Type of `this` in Function Definitions
---------------------------------------------------

```admonish tip.side.wide "Tip: Automatically global"

Methods defined this way are automatically exposed to the [global namespace][function namespaces].
```

In many cases it may be desirable to implement _methods_ for different [custom types] using
script-defined [functions].

### The Problem

Doing so is brittle and requires a lot of type checking code because there can only be one
[function] definition for the same name and arity:

```js
// Really painful way to define a method called 'do_update' on various data types
fn do_update(x) {
    switch type_of(this) {
        "i64" => this *= x,
        "string" => this.len += x,
        "bool" if this => this *= x,
        "bool" => this *= 42,
        "MyType" => this.update(x),
        "Strange-Type#Name::with_!@#symbols" => this.update(x),
        _ => throw `I don't know how to handle ${type_of(this)}`!`
    }
}
```

### The Solution

With a special syntax, it is possible to restrict a [function] to be callable only when the object
pointed to by `this` is of a certain type:

> `fn`  _type name_ `.` _method_ `(` _parameters_ ... `)  {`  ...  `}`

or in quotes if the type name is not a valid identifier itself:

> `fn`  `"`_type name string_`"` `.` _method_ `(` _parameters_ ... `)  {`  ...  `}`

Needless to say, this _typed method_ definition style is not available under [`no_object`].

~~~admonish warning.small "Type name must be the same as `type_of`"

The _type name_ specified in front of the [function] name must match the output of [`type_of`]
for the required type.
~~~

~~~admonish tip.small "Tip: `int` and `float`"
`int` can be used in place of the system integer type (usually `i64` or `i32`).

`float` can be used in place of the system floating-point type (usually `f64` or `f32`).

Using these make scripts more portable.
~~~

### Examples

```js
/// This 'do_update' can only be called on objects of type 'MyType' in method style
fn MyType.do_update(x, y) {
    this.update(x * y);
}

/// This 'do_update' can only be called on objects of type 'Strange-Type#Name::with_!@#symbols'
/// (which can be specified via 'Engine::register_type_with_name') in method style
fn "Strange-Type#Name::with_!@#symbols".do_update(x, y) {
    this.update(x * y);
}

/// Define a blanket version
fn do_update(x, y) {
    this = `${this}, ${x}, ${y}`;
}

/// This 'do_update' can only be called on integers in method style
fn int.do_update(x, y) {
    this += x * y
}

let obj = create_my_type();     // 'x' is 'MyType'

obj.type_of() == "MyType";

obj.do_update(42, 123);         // ok!

let x = 42;                     // 'x' is an integer

x.type_of() == "i64";

x.do_update(42, 123);           // ok!

let x = true;                   // 'x' is a boolean

x.type_of() == "bool";

x.do_update(42, 123);           // <- this works because there is a blanket version

// Use 'is_def_fn' with three parameters to test for typed methods

is_def_fn("MyType", "do_update", 2) == true;

is_def_fn("int", "do_update", 2) == true;
```


Bind to `this` for Module Functions
-----------------------------------

### The Problem

The _method-call_ syntax is not possible for [functions] [imported][`import`] from [modules].

```js
import "my_module" as foo;

let x = 42;

x.foo::change_value(1);     // <- syntax error
```

### The Solution

In order to call a [module] [function] as a method, it must be defined with a restriction on the
type of object pointed to by `this`:

```js
┌────────────────┐
│ my_module.rhai │
└────────────────┘

// This is a typed method function requiring 'this' to be an integer.
// Typed methods are automatically marked global when importing this module.
fn int.change_value(offset) {
    // 'this' is guaranteed to be an integer
    this += offset;
}


┌───────────┐
│ main.rhai │
└───────────┘

import "my_module";

let x = 42;

x.change_value(1);          // ok!

x == 43;
```


# fn-missing.md
Missing Function Handling
=========================

{{#include ../links.md}}

[`Engine::on_missing_function`]: https://docs.rs/rhai/{{version}}/rhai/struct.Engine.html#method.on_missing_function


~~~admonish warning.small "Requires `internals`"

This is an advanced feature that requires the [`internals`] feature to be enabled.
~~~

Normally, when a [function] or a [method] is called but not found by the [`Engine`],
the script terminates with an error.

It is possible to completely control this behavior via a special callback function
registered into an [`Engine`] via `on_missing_function`.

Using this callback, for instance, it is simple to instruct Rhai to return a default value, call a
fallback [function] on the fly, or even modify the error returned, when a non-existent [function] or
[method] is called.


Function Signature
------------------

The function signature passed to [`Engine::on_missing_function`] takes the following form.

> ```rust
> Fn(name: &str, args: &mut [&mut Dynamic], is_method_call: bool, context: EvalContext)  
>       -> Result<Option<Dynamic>, Box<EvalAltResult>>
> ```

where:

| Parameter        |         Type          | Description                                                                                                           |
| ---------------- | :-------------------: | --------------------------------------------------------------------------------------------------------------------- |
| `name`           |        `&str`         | name of the [function] called                                                                                         |
| `args`           | `&mut [&mut Dynamic]` | arguments passed to the [function]                                                                                    |
| `is_method_call` |        `bool`         | `true` if the [function] is called as a [method], which means that the first argument (the object) cannot be consumed |
| `context`        |    [`EvalContext`]    | the current _evaluation context_                                                                                      |

### Return value

Return `Some` as the value returned by the [function] call, or `None` to return the standard error.


Example
-------

```rust
engine.on_missing_function(|name, args, is_method_call, context| {
    if is_method_call && name == "greet" {
        Ok(Some(Dynamic::from("hello")))
    } else {
        Ok(None)    // fall through to standard error
    }
});
```


# fn-namespaces.md
Function Namespaces
===================

{{#include ../links.md}}


Each Function is a Separate Compilation Unit
--------------------------------------------

[Functions] in Rhai are _pure_ and they form individual _compilation units_.

This means that individual [functions] can be separated, exported, re-grouped, imported, and
generally mix-'n-matched with other completely unrelated scripts.

For example, the `AST::merge` and `AST::combine` methods (or the equivalent `+` and `+=` operators)
allow combining all [functions] in one [`AST`] into another, forming a new, unified, group of [functions].


Namespace Types
---------------

In general, there are two main types of _namespaces_ where [functions] are looked up:

| Namespace | Quantity | Source                                                                                                                                                                                                                                                    | Lookup                   | Sub-modules? | Variables? |
| --------- | :------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | :----------: | :--------: |
| Global    |   one    | <ol><li>[`AST`] being evaluated</li><li>`Engine::register_XXX` API</li><li>global registered [modules]</li><li>[functions] in [imported][`import`] [modules] marked _global_</li><li>[functions] in registered static [modules] marked _global_</li></ol> | simple name              |   ignored    |  ignored   |
| Module    |   many   | <ol><li>[Module] registered via `Engine::register_static_module`</li><li>[Module] loaded via [`import`] statement</li></ol>                                                                                                                               | namespace-qualified name |     yes      |    yes     |

### Module Namespaces

There can be multiple [module] namespaces at any time during a script evaluation, usually loaded via
the [`import`] statement.

_Static_ [module] namespaces can also be registered into an [`Engine`] via `Engine::register_static_module`.

[Functions] and [variables] in module namespaces are isolated and encapsulated within their own environments.

They must be called or accessed in a _namespace-qualified_ manner.

```js
import "my_module" as m;        // new module namespace 'm' created via 'import'

let x = m::calc_result();       // namespace-qualified function call

let y = m::MY_NUMBER;           // namespace-qualified variable/constant access

let z = calc_result();          // <- error: function 'calc_result' not found
                                //    in global namespace!
```

### Global Namespace

There is one _global_ namespace for every [`Engine`], which includes (in the following search order):

* all [functions] defined in the [`AST`] currently being evaluated,

* all native Rust functions and iterators registered via the `Engine::register_XXX` API,

* all functions and iterators defined in global [modules] that are registered into the [`Engine`]
  via `register_global_module`,

* functions defined in [modules] registered into the [`Engine`] via `register_static_module` that
  are specifically marked for exposure to the global namespace (e.g. via the `#[rhai(global)]`
  attribute in a [plugin module]).

* [functions] defined in [imported][`import`] [modules] that are specifically marked for exposure to
  the global namespace (e.g. via the `#[rhai(global)]` attribute in a [plugin module]).

Anywhere in a Rhai script, when a function call is made, the function is searched within the
global namespace, in the above search order.

Therefore, function calls in Rhai are _late_ bound &ndash; meaning that the function called cannot be
determined or guaranteed; there is no way to _lock down_ the function being called.
This aspect is very similar to JavaScript before ES6 modules.

```rust
// Compile a script into AST
let ast1 = engine.compile(
r#"
    fn get_message() {
        "Hello!"                // greeting message
    }

    fn say_hello() {
        print(get_message());   // prints message
    }

    say_hello();
"#)?;

// Compile another script with an overriding function
let ast2 = engine.compile(r#"fn get_message() { "Boo!" }"#)?;

// Combine the two AST's
ast1 += ast2;                   // 'message' will be overwritten

engine.run_ast(&ast1)?;         // prints 'Boo!'
```

Therefore, care must be taken when _cross-calling_ [functions] to make sure that the correct
[function] is called.

The only practical way to ensure that a [function] is a correct one is to use [modules] &ndash;
i.e. define the [function] in a separate [module] and then [`import`] it:

```js
┌──────────────┐
│ message.rhai │
└──────────────┘

fn get_message() { "Hello!" }


┌─────────────┐
│ script.rhai │
└─────────────┘

import "message" as msg;

fn say_hello() {
    print(msg::get_message());
}
say_hello();
```


# fn-parent-scope.md
Call a Function Within the Caller's Scope
=========================================

{{#include ../links.md}}


Peeking Out of The Pure Box
---------------------------

```admonish info.side "Only scripts"

This is only meaningful for _scripted_ [functions].

Native Rust functions can never access any [`Scope`].
```

Rhai [functions] are _pure_, meaning that they depend on on their arguments and have no access to
the calling environment.

When a [function] accesses a [variable] that is not defined within that [function]'s [`Scope`],
it raises an evaluation error.

It is possible, through a special syntax, to actually run the [function] call within the [`Scope`]
of the parent caller &ndash; i.e. the [`Scope`] that makes the [function] call &ndash; and
access/mutate [variables] defined there.


```rust
fn foo(y) {             // function accesses 'x' and 'y', but 'x' is not defined
    x += y;             // 'x' is modified in this function
    let z = 0;          // 'z' is defined in this function's scope
    x
}

let x = 1;              // 'x' is defined here in the parent scope

foo(41);                // error: variable 'x' not found

// Calling a function with a '!' causes it to run within the caller's scope

foo!(41) == 42;         // the function can access and mutate the value of 'x'!

x == 42;                // 'x' is changed!

z == 0;                 // <- error: variable 'z' not found

x.method!();            // <- syntax error: not allowed in method-call style

// Also works for function pointers

let f = foo;            // <- de-sugars to 'Fn("foo")'

call!(f, 42) == 84;     // must use function-call style

x == 84;                // 'x' is changed once again

f.call!(41);            // <- syntax error: not allowed in method-call style

// But not allowed for module functions

import "hello" as h;

h::greet!();            // <- syntax error: not allowed in namespace-qualified calls
```

```admonish danger.small "The caller's scope can be mutated"

Changes to [variables] in the calling [`Scope`] persist.

With this syntax, it is possible for a Rhai [function] to mutate its calling environment.
```

```admonish warning.small "New variables are not retained"

[Variables] or [constants] defined within the [function] are _not_ retained.
They remain local to the [function].

Although the syntax resembles a Rust _macro_ invocation, it is still a [function] call.
```


```admonish danger "Caveat emptor"

[Functions] relying on the calling [`Scope`] is often a _Very Bad Idea™_ because it makes code
almost impossible to reason about and maintain, as their behaviors are volatile and unpredictable.

Rhai [functions] are normally _pure_, meaning that you can rely on the fact that they never mutate
the outside environment.  Using this syntax breaks this guarantee.

[Functions] called in this manner behave more like macros that are expanded inline than actual
function calls, thus the syntax is also similar to Rust's macro invocations.

This usage should be at the last resort.

**YOU HAVE BEEN WARNED**.
```


# fn-ptr.md
Function Pointers
=================

{{#include ../links.md}}

```admonish question.side "Trivia"

A function pointer simply stores the _name_ of the [function] as a [string].
```

It is possible to store a _function pointer_ in a variable just like a normal value.

A function pointer is created via the `Fn` [function], which takes a [string] parameter.

Call a function pointer via the `call` method.


Short-Hand Notation
-------------------

```admonish warning.side "Not for native"

Native Rust functions cannot use this short-hand notation.
```

Having to write `Fn("foo")` in order to create a function pointer to the [function] `foo` is a chore,
so there is a short-hand available.

A function pointer to any _script-defined_ [function] _within the same script_ can be obtained simply
by referring to the [function's][function] name.

```rust
fn foo() { ... }        // function definition

let f = foo;            // function pointer to 'foo'

let f = Fn("foo");      // <- the above is equivalent to this

let g = bar;            // error: variable 'bar' not found
```

The short-hand notation is particularly useful when passing [functions] as [closure] arguments.

```rust
fn is_even(n) { n % 2 == 0 }

let array = [1, 2, 3, 4, 5];

array.filter(is_even);

array.filter(Fn("is_even"));    // <- the above is equivalent to this

array.filter(|n| n % 2 == 0);   // <- ... or this
```

Built-in Functions
------------------

The following standard methods (mostly defined in the [`BasicFnPackage`][built-in packages] but
excluded when using a [raw `Engine`]) operate on function pointers.

| Function                           | Parameter(s) | Description                                                                                      |
| ---------------------------------- | ------------ | ------------------------------------------------------------------------------------------------ |
| `name` method and property         | _none_       | returns the name of the [function] encapsulated by the function pointer                          |
| `is_anonymous` method and property | _none_       | does the function pointer refer to an [anonymous function]? Not available under [`no_function`]. |
| `call`                             | _arguments_  | calls the [function] matching the function pointer's name with the _arguments_                   |


Examples
--------

```rust
fn foo(x) { 41 + x }

let func = Fn("foo");       // use the 'Fn' function to create a function pointer

let func = foo;             // <- short-hand: equivalent to 'Fn("foo")'

print(func);                // prints 'Fn(foo)'

let func = fn_name.Fn();    // <- error: 'Fn' cannot be called in method-call style

func.type_of() == "Fn";     // type_of() as function pointer is 'Fn'

func.name == "foo";

func.call(1) == 42;         // call a function pointer with the 'call' method

foo(1) == 42;               // <- the above de-sugars to this

call(func, 1);              // normal function call style also works for 'call'

let len = Fn("len");        // 'Fn' also works with registered native Rust functions

len.call("hello") == 5;

let fn_name = "hello";      // the function name does not have to exist yet

let hello = Fn(fn_name + "_world");

hello.call(0);              // error: function not found - 'hello_world (i64)'
```


```admonish warning "Not First-Class Functions"

Beware that function pointers are _not_ first-class functions.

They are _syntactic sugar_ only, capturing only the _name_ of a [function] to call.
They do not hold the actual [functions].

The actual [function] must be defined in the appropriate [namespace][function namespace]
for the call to succeed.
```

~~~admonish warning "Global Namespace Only"

Because of their dynamic nature, function pointers cannot refer to functions in [`import`]-ed [modules].

They can only refer to [functions] within the global [namespace][function namespace].

```js
import "foo" as f;          // assume there is 'f::do_work()'

f::do_work();               // works!

let p = Fn("f::do_work");   // error: invalid function name

fn do_work_now() {          // call it from a local function
    f::do_work();
}

let p = Fn("do_work_now");

p.call();                   // works!
```
~~~


Dynamic Dispatch
----------------

The purpose of function pointers is to enable rudimentary _dynamic dispatch_, meaning to determine,
at runtime, which function to call among a group.

Although it is possible to simulate dynamic dispatch via a number and a large
[`if-then-else-if`][`if`] statement, using function pointers significantly simplifies the code.

```rust
let x = some_calculation();

// These are the functions to call depending on the value of 'x'
fn method1(x) { ... }
fn method2(x) { ... }
fn method3(x) { ... }

// Traditional - using decision variable
let func = sign(x);

// Dispatch with if-statement
if func == -1 {
    method1(42);
} else if func == 0 {
    method2(42);
} else if func == 1 {
    method3(42);
}

// Using pure function pointer
let func = if x < 0 {
    method1
} else if x == 0 {
    method2
} else if x > 0 {
    method3
};

// Dynamic dispatch
func.call(42);

// Using functions map
let map = [ method1, method2, method3 ];

let func = sign(x) + 1;

// Dynamic dispatch
map[func].call(42);
```


Bind the `this` Pointer
-----------------------

When `call` is called as a _method_ but not on a function pointer, it is possible to dynamically dispatch
to a function call while binding the object in the method call to the `this` pointer of the function.

To achieve this, pass the function pointer as the _first_ argument to `call`:

```rust
fn add(x) {                 // define function which uses 'this'
    this += x;
}

let func = add;             // function pointer to 'add'

func.call(1);               // error: 'this' pointer is not bound

let x = 41;

func.call(x, 1);            // error: function 'add (i64, i64)' not found

call(func, x, 1);           // error: function 'add (i64, i64)' not found

x.call(func, 1);            // 'this' is bound to 'x', dispatched to 'func'

x == 42;
```

Beware that this only works for [_method-call_](fn-method.md) style.
Normal function-call style cannot bind the `this` pointer (for syntactic reasons).

Therefore, obviously, binding the `this` pointer is unsupported under [`no_object`].


Call a Function Pointer within a Rust Function (as a Callback)
--------------------------------------------------------------

It is completely normal to register a Rust function with an [`Engine`] that takes parameters
whose types are function pointers.  The Rust type in question is `rhai::FnPtr`.

A function pointer in Rhai is essentially syntactic sugar wrapping the _name_ of a function
to call in script.  Therefore, the script's _execution context_ (i.e. [`NativeCallContext`])
is needed in order to call a function pointer.

```rust
use rhai::{Engine, FnPtr, NativeCallContext};

let mut engine = Engine::new();

// A function expecting a callback in form of a function pointer.
fn super_call(context: NativeCallContext, callback: FnPtr, value: i64)
                -> Result<String, Box<EvalAltResult>>
{
    // Use 'FnPtr::call_within_context' to call the function pointer using the call context.
    // 'FnPtr::call_within_context' automatically casts to the required result type.
    callback.call_within_context(&context, (value,))
    //                                     ^^^^^^^^ arguments passed in tuple
}

engine.register_fn("super_call", super_call);
```


Call a Function Pointer Directly
--------------------------------

The `FnPtr::call` method allows the function pointer to be called directly on any [`Engine`] and
[`AST`], making it possible to reuse the `FnPtr` data type in may different calls and scripting
environments.

```rust
use rhai::{Engine, FnPtr};

let engine = Engine::new();

// Compile script to AST
let ast = engine.compile(
r#"
    let test = "hello";
    |x| test + x            // this creates a closure
"#)?;

// Save the closure together with captured variables
let fn_ptr = engine.eval_ast::<FnPtr>(&ast)?;

// 'f' captures: the Engine, the AST, and the closure
let f = move |x: i64| -> Result<String, _> {
            fn_ptr.call(&engine, &ast, (x,))
        };

// 'f' can be called like a normal function
let result = f(42)?;

result == "hello42";
```


Bind to a native Rust Function
------------------------------

It is also possible to create a function pointer that binds to a native Rust function or a Rust closure.

The signature of the native Rust function takes the following form.

> ```rust
> Fn(context: NativeCallContext, args: &mut [&mut Dynamic])  
>    -> Result<Dynamic, Box<EvalAltResult>> + 'static
> ```

where:

| Parameter |         Type          | Description                                     |
| --------- | :-------------------: | ----------------------------------------------- |
| `context` | [`NativeCallContext`] | mutable reference to the current _call context_ |
| `args`    | `&mut [&mut Dynamic]` | mutable reference to list of arguments          |

When such a function pointer is used in script, the native Rust function will be called
with the arguments provided.

The Rust function should check whether the appropriate number of arguments have been passed.


# for.md
For Loop
========

{{#include ../links.md}}

Iterating through a numeric [range] or an [array], or any type with a registered [type iterator],
is provided by the `for` ... `in` loop.

There are two alternative syntaxes, one including a counter variable:

> `for` _variable_ `in` _expression_ `{` ... `}`
>
> `for (` _variable_ `,` _counter_ `)` `in` _expression_ `{` ... `}`

~~~admonish tip.small "Tip: Disable `for` loops"

`for` loops can be disabled via [`Engine::set_allow_looping`][options].
~~~

Break or Continue
-----------------

Like C, `continue` can be used to skip to the next iteration, by-passing all following statements.

`break` can be used to break out of the loop unconditionally.


For Expression
--------------

Unlike Rust, `for` statements can also be used as _expressions_.

The `break` statement takes an optional expression that provides the return value.

The default return value of a `for` expression is [`()`].

~~~admonish tip.small "Tip: Disable all loop expressions"

Loop expressions can be disabled via [`Engine::set_allow_loop_expressions`][options].
~~~

```js
let a = [42, 123, 999, 0, true, "hello", "world!", 987.6543];

// 'for' can be used just like an expression
let index = for (item, count) in a {
    // if the 'for' loop breaks here, return a specific value
    switch item.type_of() {
        "i64" if item.is_even => break count,
        "f64" if item.to_int().is_even => break count,
    }

    // ... if the 'for' loop exits here, the return value is ()
};

if index == () {
    print("Magic number not found!");
} else {
    print(`Magic number found at index ${index}!`);
}
```


Counter Variable
----------------

The counter variable, if specified, starts from zero, incrementing upwards.

```js , no_run
let a = [42, 123, 999, 0, true, "hello", "world!", 987.6543];

// Loop through the array
for (item, count) in a {
    if x.type_of() == "string" {
        continue;                   // skip to the next iteration
    }

    // 'item' contains a copy of each element during each iteration
    // 'count' increments (starting from zero) for each iteration
    print(`Item #${count + 1} = ${item}`);

    if x == 42 { break; }           // break out of for loop
}
```


# functions.md
Functions
=========

{{#include ../links.md}}

Rhai supports defining functions in script via the `fn` keyword, with a syntax that is very similar to Rust without types.

Valid function names are the same as valid [variable] names.

```rust
fn add(x, y) {
    x + y
}

fn sub(x, y,) {     // trailing comma in parameters list is OK
    x - y
}

add(2, 3) == 5;

sub(2, 3,) == -1;   // trailing comma in arguments list is OK
```

```admonish tip.small "Tip: Disable functions"

Defining functions can be disabled via the [`no_function`] feature.
```

~~~admonish tip.small "Tip: `is_def_fn`"

Use `is_def_fn` (not available under [`no_function`]) to detect if a Rhai function is defined
(and therefore callable) based on its name and the number of parameters (_arity_).

```rust
fn foo(x) { x + 1 }

is_def_fn("foo", 1) == true;

is_def_fn("foo", 0) == false;

is_def_fn("foo", 2) == false;

is_def_fn("bar", 1) == false;
```
~~~


Implicit Return
---------------

Just like in Rust, an implicit return can be used. In fact, the last statement of a block is
_always_ the block's return value regardless of whether it is terminated with a semicolon `;`.
This is different from Rust.

```rust
fn add(x, y) {      // implicit return:
    x + y;          // value of the last statement (no need for ending semicolon)
                    // is used as the return value
}

fn add2(x) {
    return x + 2;   // explicit return
}

add(2, 3) == 5;

add2(42) == 44;
```


Global Definitions Only
-----------------------

Functions can only be defined at the global level, never inside a block or another function.

Again, this is different from Rust.

```rust
// Global level is OK
fn add(x, y) {
    x + y
}

// The following will not compile
fn do_addition(x) {
    fn add_y(n) {   // <- syntax error:  cannot define inside another function
        n + y
    }

    add_y(x)
}
```


No Access to External Scope
---------------------------

Functions are not _closures_. They do not capture the calling environment and can only access their
own parameters.

They cannot access [variables] external to the function itself.

```rust
let x = 42;

fn foo() {
    x               // <- error: variable 'x' not found
}
```


But Can Call Other Functions and Access Modules
-----------------------------------------------

All functions in the same [`AST`] can call each other.

```rust
fn foo(x) {         // function defined in the global namespace
    x + 1
}

fn bar(x) {
    foo(x)          // ok! function 'foo' can be called
}
```

In addition, [modules] [imported][`import`] at global level can be accessed.

```js
import "hello" as hey;
import "world" as woo;

{
    import "x" as xyz;  // <- this module is not at global level
}                       // <- it goes away here

fn foo(x) {
    hey::process(x);    // ok! imported module 'hey' can be accessed

    print(woo::value);  // ok! imported module 'woo' can be accessed

    xyz::do_work();     // <- error: module 'xyz' not found
}
```


Automatic Global Module
-----------------------

When a [constant] is declared at global scope, it is added to a special [module] called [`global`].

Functions can access those [constants] via the special [`global`] [module].

Naturally, the automatic [`global`] [module] is not available under [`no_function`] nor [`no_module`].

```rust
const CONSTANT = 42;        // this constant is automatically added to 'global'

let hello = 1;              // variables are not added to 'global'

{
    const INNER = 0;        // this constant is not at global level
}                           // <- it goes away here

fn foo(x) {
    x * global::hello       // <- error: variable 'hello' not found in 'global'

    x * global::CONSTANT    // ok! 'CONSTANT' exists in 'global'

    x * global::INNER       // <- error: constant 'INNER' not found in 'global'
}
```


Use Before Definition Allowed
-----------------------------

Unlike C/C++, functions in Rhai can be defined _anywhere_ at global level.

A function does not need to be defined prior to being used in a script; a statement in the script
can freely call a function defined afterwards.

This is similar to Rust and many other modern languages, such as JavaScript's `function` keyword.

```rust
let x = foo(41);    // <- I can do this!

fn foo(x) {         // <- define 'foo' after use
    x + 1
}
```


Arguments are Passed by Value
-----------------------------

Functions defined in script always take [`Dynamic`] parameters (i.e. they can be of any types).
Therefore, functions with the same name and same _number_ of parameters are equivalent.

All arguments are passed by _value_, so all Rhai script-defined functions are _pure_
(i.e. they never modify their arguments).

Any update to an argument will **not** be reflected back to the caller.


```rust
fn change(s) {      // 's' is passed by value
    s = 42;         // only a COPY of 's' is changed
}

let x = 500;

change(x);

x == 500;           // 'x' is NOT changed!
```

```admonish warning.small "Rhai functions are pure"

The only possibility for a Rhai script-defined function to modify an external variable is
via the [`this`](fn-method.md) pointer.
```


# global.md
Automatic Global Module
=======================

{{#include ../links.md}}


When a [constant] is declared at global scope, it is added to a special [module] called `global`.

[Functions] can access those [constants] via the special `global` [module].

Naturally, the automatic `global` [module] is not available under [`no_function`] nor [`no_module`].

```rust
const CONSTANT = 42;        // this constant is automatically added to 'global'

{
    const INNER = 0;        // this constant is not at global level
}                           // <- it goes away here

fn foo(x) {
    x *= global::CONSTANT;  // ok! 'CONSTANT' exists in 'global'

    x * global::INNER       // <- error: constant 'INNER' not found in 'global'
}
```


Override `global`
-----------------

It is possible to _override_ the automatic global [module] by [importing][`import`] another [module]
under the name `global`.

```rust
import "foo" as global;     // import a module as 'global'

const CONSTANT = 42;        // this constant is NOT added to 'global'

fn foo(x) {
    global::CONSTANT        // <- error: constant 'CONSTANT' not found in 'global'
}
```


# if.md
If Statement
============

{{#include ../links.md}}

`if` statements follow C syntax.

```rust
if foo(x) {
    print("It's true!");
} else if bar == baz {
    print("It's true again!");
} else if baz.is_foo() {
    print("Yet again true.");
} else if foo(bar - baz) {
    print("True again... this is getting boring.");
} else {
    print("It's finally false!");
}
```

~~~admonish warning.small "Braces are mandatory"

Unlike C, the condition expression does _not_ need to be enclosed in parentheses `(`...`)`, but all
branches of the `if` statement must be enclosed within braces `{`...`}`, even when there is only
one statement inside the branch.

Like Rust, there is no ambiguity regarding which `if` clause a branch belongs to.

```rust
// Rhai is not C!
if (decision) print(42);
//            ^ syntax error, expecting '{'
```
~~~


If Expression
-------------

Like Rust, `if` statements can also be used as _expressions_, replacing the `? :` conditional
operators in other C-like languages.

~~~admonish tip.small "Tip: Disable `if` expressions"

`if` expressions can be disabled via [`Engine::set_allow_if_expression`][options].
~~~

```rust
// The following is equivalent to C: int x = 1 + (decision ? 42 : 123) / 2;
let x = 1 + if decision { 42 } else { 123 } / 2;
x == 22;

let x = if decision { 42 }; // no else branch defaults to '()'
x == ();
```

~~~admonish danger.small "Statement before expression"

Beware that, like Rust, `if` is parsed primarily as a statement where it makes sense.
This is to avoid surprises.

```rust
fn index_of(x) {
    // 'if' is parsed primarily as a statement
    if this.contains(x) {
        return this.find_index(x)
    }

    -1
}
```

The above will not be parsed as a single expression:

```rust
fn index_of(x) {
    if this.contains(x) { return this.find_index(x) } - 1
    //                          error due to '() - 1' ^
}

```

To force parsing as an expression, parentheses are required:

```rust
fn calc_index(b, offset) {
    (if b { 1 } else { 0 }) + offset
//  ^---------------------^ parentheses
}
```
~~~


# in.md
In Operator
===========

{{#include ../links.md}}

```admonish question.side.wide "Trivia"

The `in` operator is simply syntactic sugar for a call to the `contains` function.

Similarly, `!in` is a call to `!contains`.
```

The `in` operator is used to check for _containment_ &ndash; i.e. whether a particular collection
data type _contains_ a particular item.

Similarly, `!in` is used to check for non-existence &ndash; i.e. it is `true` if a particular
collection data type does _not_ contain a particular item.

```rust
42 in array;

array.contains(42);     // <- the above is equivalent to this

123 !in array;

!array.contains(123);   // <- the above is equivalent to this
```


Built-in Support for Standard Data Types
----------------------------------------

|    Data type    |              Check for              |
| :-------------: | :---------------------------------: |
| Numeric [range] |           integer number            |
|     [Array]     |           contained item            |
|  [Object map]   |            property name            |
|    [String]     | [sub-string][string] or [character] |


Examples
--------

```rust
let array = [1, "abc", 42, ()];

42 in array == true;                // check array for item

let map = #{
    foo: 42,
    bar: true,
    baz: "hello"
};

"foo" in map == true;               // check object map for property name

'w' in "hello, world!" == true;     // check string for character

'w' !in "hello, world!" == false;

"wor" in "hello, world" == true;    // check string for sub-string

42 in -100..100 == true;            // check range for number
```


Array Items Comparison
----------------------

The default implementation of the `in` operator for [arrays] uses the `==` operator (if defined)
to compare items.

~~~admonish warning.small "`==` defaults to `false`"

For a [custom type], `==` defaults to `false` when comparing it with a value of of the same type.

See the section on [_Logic Operators_](logic.md) for more details.
~~~

```rust
let ts = new_ts();                  // assume 'new_ts' returns a custom type

let array = [1, 2, 3, ts, 42, 999];
//                    ^^ custom type

42 in array == true;                // 42 cannot be compared with 'ts'
                                    // so it defaults to 'false'
                                    // because == operator is not defined
```


Custom Implementation of `contains`
-----------------------------------

The `in` and `!in` operators map directly to a call to a function `contains` with the two operands switched.

```rust
// This expression...
item in container

// maps to this...
contains(container, item)

// or...
container.contains(item)
```

Support for the `in` and `!in` operators can be easily extended to other types by registering a
custom binary function named `contains` with the correct parameter types.

Since `!in` maps to `!(... in ...)`, `contains` is enough to support both operators.

```rust
let mut engine = Engine::new();

engine.register_type::<TestStruct>()
      .register_fn("new_ts", || TestStruct::new())
      .register_fn("contains", |ts: &mut TestStruct, item: i64| -> bool {
          // Remember the parameters are switched from the 'in' expression
          ts.contains(item)
      });

// Now the 'in' operator can be used for 'TestStruct' and integer

engine.run(
r#"
    let ts = new_ts();

    if 42 in ts {                   // this calls 'ts.contains(42)'
        print("I got 42!");
    } else if 123 !in ts {          // this calls '!ts.contains(123)'
        print("I ain't got 123!");
    }

    let err = "hello" in ts;        // <- runtime error: 'contains' not found
                                    //    for 'TestStruct' and string
"#)?;
```


# iter.md
Standard Iterable Types
========================

{{#include ../links.md}}

Certain [standard types] are iterable via a [`for`] statement.


Iterate Through Arrays
----------------------

Iterating through an [array] yields cloned _copies_ of each element.

```rust
let a = [1, 3, 5, 7, 9, 42];

// Loop through the array
for x in a {
    if x > 10 { continue; }         // skip to the next iteration

    print(x);

    if x == 42 { break; }           // break out of for loop
}
```

Iterate Through Strings
-----------------------

Iterating through a [string] yields individual [characters].

The `chars` method also allow iterating through characters in a [string], optionally accepting the
character position to start from (counting from the end if negative), as well as the number of
characters to iterate (defaults to all).

`char` also accepts a [range] which can be created via the `..` (exclusive) and `..=` (inclusive) operators.

```rust
let s = "hello, world!";

// Iterate through all the characters.
for ch in s {
    print(ch);
}

// Iterate starting from the 3rd character and stopping at the 7th.
for ch in s.chars(2, 5) {
    if ch > 'z' { continue; }       // skip to the next iteration

    print(ch);

    if x == '@' { break; }          // break out of for loop
}

// Iterate starting from the 3rd character and stopping at the end.
for ch in s.chars(2..s.len) {
    if ch > 'z' { continue; }       // skip to the next iteration

    print(ch);

    if x == '@' { break; }          // break out of for loop
}
```


Iterate Through Numeric Ranges
------------------------------

[Ranges] are created via the `..` (exclusive) and `..=` (inclusive) operators.

The `range` function similarly creates exclusive [ranges], plus allowing optional step values.

```rust
// Iterate starting from 0 and stopping at 49
// The step is assumed to be 1 when omitted for integers
for x in 0..50 {
    if x > 10 { continue; }         // skip to the next iteration

    print(x);

    if x == 42 { break; }           // break out of for loop
}

// The 'range' function is just the same
for x in range(0, 50) {
    if x > 10 { continue; }         // skip to the next iteration

    print(x);

    if x == 42 { break; }           // break out of for loop
}

// The 'range' function also takes a step
for x in range(0, 50, 3) {          // step by 3
    if x > 10 { continue; }         // skip to the next iteration

    print(x);

    if x == 42 { break; }           // break out of for loop
}

// The 'range' function can also step backwards
for x in range(50..0, -3) {         // step down by -3
    if x < 10 { continue; }         // skip to the next iteration

    print(x);

    if x == 42 { break; }           // break out of for loop
}

// It works also for floating-point numbers
for x in range(5.0, 0.0, -2.0) {    // step down by -2.0
    if x < 10 { continue; }         // skip to the next iteration

    print(x);

    if x == 4.2 { break; }          // break out of for loop
}
```

Iterate Through Bit-Fields
--------------------------

The `bits` function allows iterating through an integer as a [bit-field].

`bits` optionally accepts the bit number to start from (counting from the most-significant-bit if
negative), as well as the number of bits to iterate (defaults all).

`bits` also accepts a [range] which can be created via the `..` (exclusive) and `..=` (inclusive) operators.

```js , no_run
let x = 0b_1001110010_1101100010_1100010100;
let num_on = 0;

// Iterate through all the bits
for bit in x.bits() {
    if bit { num_on += 1; }
}

print(`There are ${num_on} bits turned on!`);

const START = 3;

// Iterate through all the bits from 3 through 12
for (bit, index) in x.bits(START, 10) {
    print(`Bit #${index} is ${if bit { "ON" } else { "OFF" }}!`);

    if index >= 7 { break; }        // break out of for loop
}

// Iterate through all the bits from 3 through 12
for (bit, index) in x.bits(3..=12) {
    print(`Bit #${index} is ${if bit { "ON" } else { "OFF" }}!`);

    if index >= 7 { break; }        // break out of for loop
}
```

Iterate Through Object Maps
---------------------------

Two methods, `keys` and `values`, return [arrays] containing cloned _copies_
of all property names and values of an [object map], respectively.

These [arrays] can be iterated.

```rust
let map = #{a:1, b:3, c:5, d:7, e:9};

// Property names are returned in unsorted, random order
for x in map.keys() {
    if x > 10 { continue; }         // skip to the next iteration

    print(x);

    if x == 42 { break; }           // break out of for loop
}

// Property values are returned in unsorted, random order
for val in map.values() {
    print(val);
}
```


# iterator.md
Make a Custom Type Iterable
===========================

{{#include ../links.md}}

```admonish info.side "Built-in type iterators"

Type iterators are already defined for built-in [standard types] such as [strings], [ranges],
[bit-fields], [arrays] and [object maps].

That's why they can be used with the [`for`] loop.
```

If a [custom type] is iterable, the [`for`] loop can be used to iterate through
its items in sequence, as long as it has a _type iterator_ registered.

`Engine::register_iterator<T>` allows registration of a type iterator for any type
that implements `IntoIterator`.

With a type iterator registered, the [custom type] can be iterated through.

```rust
// Custom type
#[derive(Debug, Clone)]
struct TestStruct { fields: Vec<i64> }

// Implement 'IntoIterator' trait
impl IntoIterator<Item = i64> for TestStruct {
    type Item = i64;
    type IntoIter = std::vec::IntoIter<Self::Item>;

    fn into_iter(self) -> Self::IntoIter {
        self.fields.into_iter()
    }
}

let mut engine = Engine::new();

// Register API and type iterator for 'TestStruct'
engine.register_type_with_name::<TestStruct>("TestStruct")
      .register_fn("new_ts", || TestStruct { fields: vec![1, 2, 3, 42] })
      .register_iterator::<TestStruct>();

// 'TestStruct' is now iterable
engine.run(
"
    for value in new_ts() {
        ...
    }
")?;
```

```admonish tip.small "Tip: Fallible type iterators"

`Engine::register_iterator_result` allows registration of a _fallible_ type iterator &ndash;
i.e. an iterator that returns `Result<T, Box<EvalAltResult>>`.

On in very rare situations will this be necessary though.
```


# json.md
Parse an Object Map from JSON
=============================

{{#include ../links.md}}

Do It Without `serde`
---------------------

```admonish info.side.wide "Object map vs. JSON"

A valid JSON object hash does not start with a hash character `#` while a Rhai [object map] does.
That's the only difference!
```

The syntax for an [object map] is extremely similar to the JSON representation of a object hash,
with the exception of `null` values which can technically be mapped to [`()`].

Use the `Engine::parse_json` method to parse a piece of JSON into an [object map].

```rust
// JSON string - notice that JSON property names are always quoted
//               notice also that comments are acceptable within the JSON string
let json = r#"{
                "a": 1,                 // <- this is an integer number
                "b": true,
                "c": 123.0,             // <- this is a floating-point number
                "$d e f!": "hello",     // <- any text can be a property name
                "^^^!!!": [1,42,"999"], // <- value can be array or another hash
                "z": null               // <- JSON 'null' value
              }"#;

// Parse the JSON expression as an object map
// Set the second boolean parameter to true in order to map 'null' to '()'
let map = engine.parse_json(json, true)?;

map.len() == 6;       // 'map' contains all properties in the JSON string

// Put the object map into a 'Scope'
let mut scope = Scope::new();
scope.push("map", map);

let result = engine.eval_with_scope::<i64>(&mut scope, r#"map["^^^!!!"].len()"#)?;

result == 3;          // the object map is successfully used in the script
```

```admonish warning.small "Warning: Must be object hash"

The JSON text must represent a single object hash &ndash; i.e. must be wrapped within braces
`{`...`}`.

It cannot be a primitive type (e.g. number, string etc.).
Otherwise it cannot be converted into an [object map] and a type error is returned.
```

```admonish note.small "Representation of numbers"

JSON numbers are all floating-point while Rhai supports integers (`INT`) and floating-point (`FLOAT`)
(except under [`no_float`]).

Most common generators of JSON data distinguish between integer and floating-point values by always
serializing a floating-point number with a decimal point (i.e. `123.0` instead of `123` which is
assumed to be an integer).

This style can be used successfully with Rhai [object maps].
```

Sub-objects are handled transparently by `Engine::parse_json`.

It is _not_ necessary to replace `{` with `#{` in order to fake a Rhai [object map] literal.

```rust
// JSON with sub-object 'b'.
let json = r#"{"a":1, "b":{"x":true, "y":false}}"#;

// 'parse_json' handles this just fine.
let map = engine.parse_json(json, false)?;

// 'map' contains two properties: 'a' and 'b'
map.len() == 2;
```

```admonish question "TL;DR &ndash; How is it done?"

Internally, `Engine::parse_json` _cheats_ by treating the JSON text as a Rhai script.

That is why it even supports [comments] and arithmetic expressions in the JSON text,
although it is not a good idea to rely on non-standard JSON formats.

A [token remap filter] is used to convert `{` into `#{` and `null` to [`()`].
```


Use `serde`
-----------

```admonish info.side "See also"

See _[Serialization/ Deserialization of `Dynamic` with `serde`][`serde`]_ for more details.
```

Remember, `Engine::parse_json` is nothing more than a _cheap_ alternative to true JSON parsing.

If strict correctness is needed, or for more configuration possibilities, turn on the
[`serde`][features] feature to pull in [`serde`](https://crates.io/crates/serde) which enables
serialization and deserialization to/from multiple formats, including JSON.

Beware, though... the [`serde`](https://crates.io/crates/serde) crate is quite heavy.


# keywords.md
Keywords
========

{{#include ../links.md}}

The following are reserved keywords in Rhai.

| Active keywords                                                            | Reserved keywords                                          | Usage                               |     Inactive under feature     |
| -------------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------- | :----------------------------: |
| `true`, `false`                                                            |                                                            | [constants]                         |                                |
| [`let`][variable], [`const`][constant]                                     | `var`, `static`                                            | [variables]                         |                                |
| `is_shared`                                                                |                                                            | _shared_ values                     |         [`no_closure`]         |
|                                                                            | `is`                                                       | type checking                       |                                |
| [`if`], [`else`][`if`]                                                     | `goto`                                                     | control flow                        |                                |
| [`switch`]                                                                 | `match`, `case`                                            | switching and matching              |                                |
| [`do`], [`while`], [`loop`], `until`, [`for`], [`in`], `continue`, `break` |                                                            | looping                             |                                |
| [`fn`][function], [`private`], `is_def_fn`, `this`                         | `public`, `protected`, `new`                               | [functions]                         |        [`no_function`]         |
| [`return`]                                                                 |                                                            | return values                       |                                |
| [`throw`], [`try`], [`catch`]                                              |                                                            | [throw/catch][`catch`] [exceptions] |                                |
| [`import`], [`export`], `as`                                               | `use`, `with`, `module`, `package`, `super`                | [modules]                           |         [`no_module`]          |
| [`global`]                                                                 |                                                            | automatic global [module]           | [`no_function`], [`no_module`] |
| [`Fn`][function pointer], `call`, [`curry`][currying]                      |                                                            | [function pointers]                 |                                |
|                                                                            | `spawn`, `thread`, `go`, `sync`, `async`, `await`, `yield` | threading/async                     |                                |
| [`type_of`], [`print`], [`debug`], [`eval`], `is_def_var`                  |                                                            | special functions                   |                                |
|                                                                            | `default`, `void`, `null`, `nil`                           | special values                      |                                |

```admonish warning.small
Keywords cannot become the name of a [function] or [variable], even when they are
[disabled][disable keywords and operators].
```


# logic.md
Logic Operators
===============

{{#include ../links.md}}


Comparison Operators
--------------------

| Operator | Description<br/>(`x` _operator_ `y`) | `x`, `y` same type or are numeric | `x`, `y` different types |
| :------: | ------------------------------------ | :-------------------------------: | :----------------------: |
|   `==`   | `x` is equals to `y`                 |       error if not defined        |  `false` if not defined  |
|   `!=`   | `x` is not equals to `y`             |       error if not defined        |  `true` if not defined   |
|   `>`    | `x` is greater than `y`              |       error if not defined        |  `false` if not defined  |
|   `>=`   | `x` is greater than or equals to `y` |       error if not defined        |  `false` if not defined  |
|   `<`    | `x` is less than `y`                 |       error if not defined        |  `false` if not defined  |
|   `<=`   | `x` is less than or equals to `y`    |       error if not defined        |  `false` if not defined  |

Comparison operators between most values of the same type are built in for all [standard types].

Others are defined in the [`LogicPackage`][built-in packages] but excluded when using a [raw `Engine`].


### Floating-point numbers interoperate with integers

Comparing a floating-point number (`FLOAT`) with an integer is also supported.

```rust
42 == 42.0;         // true

42.0 == 42;         // true

42.0 > 42;          // false

42 >= 42.0;         // true

42.0 < 42;          // false
```

### Decimal numbers interoperate with integers

Comparing a [`Decimal`][rust_decimal] number with an integer is also supported.

```rust
let d = parse_decimal("42");

42 == d;            // true

d == 42;            // true

d > 42;             // false

42 >= d;            // true

d < 42;             // false
```

### Strings interoperate with characters

Comparing a [string] with a [character] is also supported, with the character first turned into a
[string] before performing the comparison.

```rust
'x' == "x";         // true

"" < 'a';           // true

'x' > "hello";      // false
```

### Comparing different types defaults to `false`

Comparing two values of _different_ data types defaults to `false` unless the appropriate operator
functions have been registered.

The exception is `!=` (not equals) which defaults to `true`. This is in line with intuition.

```rust
42 > "42";          // false: i64 cannot be compared with string

42 <= "42";         // false: i64 cannot be compared with string

let ts = new_ts();  // custom type

ts == 42;           // false: different types cannot be compared

ts != 42;           // true: different types cannot be compared

ts == ts;           // error: '==' not defined for the custom type
```

### Safety valve: Comparing different _numeric_ types has no default

Beware that the above default does _NOT_ apply to numeric values of different types
(e.g. comparison between `i64` and `u16`, `i32` and `f64`) &ndash; when multiple numeric types are
used it is too easy to mess up and for subtle errors to creep in.

```rust
// Assume variable 'x' = 42_u16, 'y' = 42_u16 (both types of u16)

x == y;             // true: '==' operator for u16 is built-in

x == "hello";       // false: different non-numeric operand types default to false

x == 42;            // error: ==(u16, i64) not defined, no default for numeric types

42 == y;            // error: ==(i64, u16) not defined, no default for numeric types
```

### Caution: Beware operators for custom types

```admonish tip.side.wide "Tip: Always the full set"

It is strongly recommended that, when defining operators for [custom types], always define the
**full set** of six operators together, or at least the `==` and `!=` pair.
```

Operators are completely separate from each other.  For example:

* `!=` does not equal `!(==)`

* `>` does not equal `!(<=)`

* `<=` does not equal `<` plus `==`

* `<=` does not imply `<`

Therefore, if a [custom type] misses an [operator] definition, it simply raises an error
or returns the default.

This behavior can be counter-intuitive.

```rust
let ts = new_ts();  // custom type with '<=' and '==' defined

ts <= ts;           // true: '<=' defined

ts < ts;            // error: '<' not defined, even though '<=' is

ts == ts;           // true: '==' defined

ts != ts;           // error: '!=' not defined, even though '==' is
```


Boolean Operators
-----------------

```admonish note.side

All boolean operators are [built in][built-in operators] for the `bool` data type.
```

|    Operator    | Description | Arity  | Short-circuits? |
| :------------: | :---------: | :----: | :-------------: |
| `!` _(prefix)_ |    _NOT_    | unary  |       no        |
|      `&&`      |    _AND_    | binary |     **yes**     |
|      `&`       |    _AND_    | binary |       no        |
|     `\|\|`     |    _OR_     | binary |     **yes**     |
|      `\|`      |    _OR_     | binary |       no        |

Double boolean operators `&&` and `||` _short-circuit_ &ndash; meaning that the second operand will not be evaluated
if the first one already proves the condition wrong.

Single boolean operators `&` and `|` always evaluate both operands.

```rust
a() || b();         // b() is not evaluated if a() is true

a() && b();         // b() is not evaluated if a() is false

a() | b();          // both a() and b() are evaluated

a() & b();          // both a() and b() are evaluated
```


Null-Coalescing Operator
------------------------

| Operator |  Description  | Arity  | Short-circuits? |
| :------: | :-----------: | :----: | :-------------: |
|   `??`   | Null-coalesce | binary |       yes       |

The null-coalescing operator (`??`) returns the first operand if it is not [`()`], or the second
operand if the first operand is [`()`].

It _short-circuits_  &ndash; meaning that the second operand will not be evaluated if the first
operand is not [`()`].

```rust
a ?? b              // returns 'a' if it is not (), otherwise 'b'

a() ?? b();         // b() is only evaluated if a() is ()
```

~~~admonish tip.small "Tip: Default value for object map property"

Use the null-coalescing operator to implement default values for non-existent [object map] properties.

```rust
let map = #{ foo: 42 };

// Regular property access
let x = map.foo;            // x == 42

// Non-existent property
let x = map.bar;            // x == ()

// Default value for property
let x = map.bar ?? 42;      // x == 42
```
~~~

### Short-circuit loops and early returns

The following statements are allowed to follow the null-coalescing operator:

* `break`
* `continue`
* [`return`]
* [`throw`]

This means that you can use the null-coalescing operator to short-circuit loops and/or
early-return from functions when the value tested is [`()`].

```rust
let total = 0;

for value in list {
    // Whenever 'calculate' returns '()', the loop stops
    total += calculate(value) ?? break;
}
```


# loop.md
Infinite Loop
=============

{{#include ../links.md}}

Infinite loops follow Rust syntax.

Like Rust, `continue` can be used to skip to the next iteration, by-passing all following statements;
`break` can be used to break out of the loop unconditionally.

~~~admonish tip.small "Tip: Disable `loop`"

`loop` can be disabled via [`Engine::set_allow_looping`][options].
~~~

```rust
let x = 10;

loop {
    x -= 1;

    if x > 5 { continue; }  // skip to the next iteration

    print(x);

    if x == 0 { break; }    // break out of loop
}
```

~~~admonish danger.small "Remember the `break` statement"

A `loop` statement without a `break` statement inside its loop block is infinite.
There is no way for the loop to stop iterating.
~~~


Loop Expression
---------------

Like Rust, `loop` statements can also be used as _expressions_.

The `break` statement takes an optional expression that provides the return value.

The default return value of a `loop` expression is [`()`].

~~~admonish tip.small "Tip: Disable all loop expressions"

Loop expressions can be disabled via [`Engine::set_allow_loop_expressions`][options].
~~~

```js
let x = 0;

// 'loop' can be used just like an expression
let result = loop {
    if is_magic_number(x) {
        // if the loop breaks here, return a specific value
        break get_magic_result(x);
    }

    x += 1;

    // ... if the loop exits here, the return value is ()
};

if result == () {
    print("Magic number not found!");
} else {
    print(`Magic result = ${result}!`);
}
```


# num-fn.md
Numeric Functions
=================

{{#include ../links.md}}


Integer Functions
-----------------

The following standard functions are defined.

| Function                      | Not available under |                 Package                  | Description                                                      |
| ----------------------------- | :-----------------: | :--------------------------------------: | ---------------------------------------------------------------- |
| `is_odd` method and property  |                     | [`ArithmeticPackage`][built-in packages] | returns `true` if the value is an odd number, otherwise `false`  |
| `is_even` method and property |                     | [`ArithmeticPackage`][built-in packages] | returns `true` if the value is an even number, otherwise `false` |
| `min`                         |                     |   [`LogicPackage`][built-in packages]    | returns the smaller of two numbers                               |
| `max`                         |                     |   [`LogicPackage`][built-in packages]    | returns the larger of two numbers                                |
| `to_float`                    |    [`no_float`]     | [`BasicMathPackage`][built-in packages]  | convert the value into `f64` (`f32` under [`f32_float`])         |
| `to_decimal`                  |   non-[`decimal`]   | [`BasicMathPackage`][built-in packages]  | convert the value into [`Decimal`][rust_decimal]                 |


Signed Numeric Functions
------------------------

The following standard functions are defined in the [`ArithmeticPackage`][built-in packages]
(excluded when using a [raw `Engine`]) and operate on `i8`, `i16`, `i32`, `i64`, `f32`, `f64` and
[`Decimal`][rust_decimal] (requires [`decimal`]) only.

| Function                      | Description                                                    |
| ----------------------------- | -------------------------------------------------------------- |
| `abs`                         | absolute value                                                 |
| `sign`                        | returns (`INT`) −1 if negative, &plus;1 if positive, 0 if zero |
| `is_zero` method and property | returns `true` if the value is zero, otherwise `false`         |


Floating-Point Functions
------------------------

The following standard functions are defined in the [`BasicMathPackage`][built-in packages]
(excluded when using a [raw `Engine`]) and operate on `f64` (`f32` under [`f32_float`]) and
[`Decimal`][rust_decimal] (requires [`decimal`]) only.

| Category         | Supports `Decimal` | Functions                                                                                |
| ---------------- | :----------------: | ---------------------------------------------------------------------------------------- |
| Trigonometry     |        yes         | `sin`, `cos`, `tan`                                                                      |
| Trigonometry     |       **no**       | `sinh`, `cosh`, `tanh` in radians, `hypot(`_x_`,`_y_`)`                                  |
| Arc-trigonometry |       **no**       | `asin`, `acos`, `atan(`_v_`)`, `atan(`_x_`,`_y_`)`, `asinh`, `acosh`, `atanh` in radians |
| Square root      |        yes         | `sqrt`                                                                                   |
| Exponential      |        yes         | `exp` (base _e_)                                                                         |
| Logarithmic      |        yes         | `ln` (base _e_)                                                                          |
| Logarithmic      |        yes         | `log` (base 10)                                                                          |
| Logarithmic      |       **no**       | `log(`_x_`,`_base_`)`                                                                    |
| Rounding         |        yes         | `floor`, `ceiling`, `round`, `int`, `fraction` methods and properties                    |
| Conversion       |        yes         | [`to_int`], [`to_decimal`] (requires [`decimal`]), [`to_float`] (not under [`no_float`]) |
| Conversion       |       **no**       | `to_degrees`, `to_radians`                                                               |
| Comparison       |        yes         | `min`, `max` (also inter-operates with integers)                                         |
| Testing          |       **no**       | `is_nan`, `is_finite`, `is_infinite` methods and properties                              |


Decimal Rounding Functions
--------------------------

The following rounding methods are defined in the [`BasicMathPackage`][built-in packages]
(excluded when using a [raw `Engine`]) and operate on [`Decimal`][rust_decimal] only,
which requires the [`decimal`] feature.

| Rounding type     | Behavior                                    | Methods                                                      |
| ----------------- | ------------------------------------------- | ------------------------------------------------------------ |
| None              |                                             | `floor`, `ceiling`, `int`, `fraction` methods and properties |
| Banker's rounding | round to integer                            | `round` method and property                                  |
| Banker's rounding | round to specified number of decimal points | `round(`_decimal points_`)`                                  |
| Round up          | away from zero                              | `round_up(`_decimal points_`)`                               |
| Round down        | towards zero                                | `round_down(`_decimal points_`)`                             |
| Round half-up     | mid-point away from zero                    | `round_half_up(`_decimal points_`)`                          |
| Round half-down   | mid-point towards zero                      | `round_half_down(`_decimal points_`)`                        |


Parsing Functions
-----------------

The following standard functions are defined in the [`BasicMathPackage`][built-in packages]
(excluded when using a [raw `Engine`]) to parse numbers.

| Function          |        No available under        | Description                                                                                   |
| ----------------- | :------------------------------: | --------------------------------------------------------------------------------------------- |
| [`parse_int`]     |                                  | converts a [string] to `INT` with an optional radix                                           |
| [`parse_float`]   | [`no_float`] and non-[`decimal`] | converts a [string] to `FLOAT` ([`Decimal`][rust_decimal] under [`no_float`] and [`decimal`]) |
| [`parse_decimal`] |         non-[`decimal`]          | converts a [string] to [`Decimal`][rust_decimal]                                              |


Formatting Functions
--------------------

The following standard functions are defined in the [`BasicStringPackage`][built-in packages]
(excluded when using a [raw `Engine`]) to convert integer numbers into a [string] of hex, octal
or binary representations.

| Function      | Description                          |
| ------------- | ------------------------------------ |
| [`to_binary`] | converts an integer number to binary |
| [`to_octal`]  | converts an integer number to octal  |
| [`to_hex`]    | converts an integer number to hex    |

These formatting functions are defined for all available integer numbers &ndash; i.e. `INT`, `u8`,
`i8`, `u16`, `i16`, `u32`, `i32`, `u64`, `i64`, `u128` and `i128` unless disabled by feature flags.


Floating-point Constants
------------------------

The following functions return standard mathematical constants.

| Function | Description               |
| -------- | ------------------------- |
| `PI`     | returns the value of &pi; |
| `E`      | returns the value of _e_  |


Numerical Functions for Scientific Computing
--------------------------------------------

Check out the [`rhai-sci`] crate for more numerical functions.


# num-op.md
Numeric Operators
=================

{{#include ../links.md}}

Numeric operators generally follow C styles.

Unary Operators
---------------

| Operator | Description |
| :------: | ----------- |
|   `+`    | positive    |
|   `-`    | negative    |

```rust
let number = +42;

number = -5;

number = -5 - +5;

-(-42) == +42;      // two '-' equals '+'
                    // beware: '++' and '--' are reserved symbols
```

Binary Operators
----------------

|  Operator   | Description                                                      | Result type | `INT` |        `FLOAT`         | [`Decimal`][rust_decimal] |
| :---------: | ---------------------------------------------------------------- | :---------: | :---: | :--------------------: | :-----------------------: |
|  `+`, `+=`  | plus                                                             |   numeric   |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|  `-`, `-=`  | minus                                                            |   numeric   |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|  `*`, `*=`  | multiply                                                         |   numeric   |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|  `/`, `/=`  | divide (integer division if acting on integer types)             |   numeric   |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|  `%`, `%=`  | modulo (remainder)                                               |   numeric   |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
| `**`, `**=` | power/exponentiation                                             |   numeric   |  yes  | yes, also `FLOAT**INT` |          **no**           |
| `<<`, `<<=` | left bit-shift (if negative number of bits, shift right instead) |   numeric   |  yes  |         **no**         |          **no**           |
| `>>`, `>>=` | right bit-shift (if negative number of bits, shift left instead) |   numeric   |  yes  |         **no**         |          **no**           |
|  `&`, `&=`  | bit-wise _And_                                                   |   numeric   |  yes  |         **no**         |          **no**           |
| `\|`, `\|=` | bit-wise _Or_                                                    |   numeric   |  yes  |         **no**         |          **no**           |
|  `^`, `^=`  | bit-wise _Xor_                                                   |   numeric   |  yes  |         **no**         |          **no**           |
|    `==`     | equals to                                                        |   `bool`    |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|    `!=`     | not equals to                                                    |   `bool`    |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|     `>`     | greater than                                                     |   `bool`    |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|    `>=`     | greater than or equals to                                        |   `bool`    |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|     `<`     | less than                                                        |   `bool`    |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|    `<=`     | less than or equals to                                           |   `bool`    |  yes  |  yes, also with `INT`  |   yes, also with `INT`    |
|    `..`     | exclusive range                                                  |   [range]   |  yes  |         **no**         |          **no**           |
|    `..=`    | inclusive range                                                  |   [range]   |  yes  |         **no**         |          **no**           |


Examples
--------

```rust
let x = (1 + 2) * (6 - 4) / 2;  // arithmetic, with parentheses

let reminder = 42 % 10;         // modulo

let power = 42 ** 2;            // power

let left_shifted = 42 << 3;     // left shift

let right_shifted = 42 >> 3;    // right shift

let bit_op = 42 | 99;           // bit masking
```


Floating-Point Interoperates with Integers
------------------------------------------

When one of the operands to a binary arithmetic [operator] is floating-point, it works with `INT` for
the other operand and the result is floating-point.

```rust
let x = 41.0 + 1;               // 'FLOAT' + 'INT'

type_of(x) == "f64";            // result is 'FLOAT'

let x = 21 * 2.0;               // 'FLOAT' * 'INT'

type_of(x) == "f64";

(x == 42) == true;              // 'FLOAT' == 'INT'

(10 < x) == true;               // 'INT' < 'FLOAT'
```


Decimal Interoperates with Integers
-----------------------------------

When one of the operands to a binary arithmetic [operator] is [`Decimal`][rust_decimal],
it works with `INT` for the other operand and the result is [`Decimal`][rust_decimal].

```rust
let d = parse_decimal("2");

let x = d + 1;                  // 'Decimal' + 'INT'

type_of(x) == "decimal";        // result is 'Decimal'

let x = 21 * d;                 // 'Decimal' * 'INT'

type_of(x) == "decimal";

(x == 42) == true;              // 'Decimal' == 'INT'

(10 < x) == true;               // 'INT' < 'Decimal'
```


Unary Before Binary
-------------------

In Rhai, unary operators take [precedence] over binary operators.  This is especially important to
remember when handling operators such as `**` which in some languages bind tighter than the unary
`-` operator.

```rust
-2 + 2 == 0;

-2 - 2 == -4;

-2 * 2 == -4;

-2 / 2 == -1;

-2 % 2 == 0;

-2 ** 2 = 4;            // means: (-2) ** 2
                        // in some languages this means: -(2 ** 2)
```


# numbers.md
Numbers
=======

{{#include ../links.md}}


Integers
--------

```admonish tip.side "Tip: Bit-fields"

Integers can also be conveniently manipulated as [bit-fields].
```

Integer numbers follow C-style format with support for decimal, binary (`0b`), octal (`0o`) and hex (`0x`) notations.

The default system integer type (also aliased to `INT`) is `i64`. It can be turned into `i32` via the [`only_i32`] feature.


Floating-Point Numbers
----------------------

```admonish tip.side "Tip: Notations"

Both decimal and scientific notations can be used to represent floating-point numbers.
```

Floating-point numbers are also supported if not disabled with [`no_float`].

The default system floating-point type is `f64` (also aliased to `FLOAT`).
It can be turned into `f32` via the [`f32_float`] feature.


`Decimal` Numbers
-----------------

When rounding errors cannot be accepted, such as in financial calculations, the [`decimal`] feature
turns on support for the [`Decimal`][rust_decimal] type, which is a fixed-precision floating-point
number with no rounding errors.


Number Literals
---------------

`_` separators can be added freely and are ignored within a number &ndash; except at the very beginning or right after
a decimal point (`.`).

| Sample             | Format                    | Value type |  [`no_float`]  | [`no_float`] + [`decimal`] |
| ------------------ | ------------------------- | :--------: | :------------: | :------------------------: |
| `_123`             | _improper separator_      |            |                |                            |
| `123_345`, `-42`   | decimal                   |   `INT`    |     `INT`      |           `INT`            |
| `0o07_76`          | octal                     |   `INT`    |     `INT`      |           `INT`            |
| `0xab_cd_ef`       | hex                       |   `INT`    |     `INT`      |           `INT`            |
| `0b0101_1001`      | binary                    |   `INT`    |     `INT`      |           `INT`            |
| `123._456`         | _improper separator_      |            |                |                            |
| `123_456.78_9`     | normal floating-point     |  `FLOAT`   | _syntax error_ | [`Decimal`][rust_decimal]  |
| `-42.`             | ending with decimal point |  `FLOAT`   | _syntax error_ | [`Decimal`][rust_decimal]  |
| `123_456_.789e-10` | scientific notation       |  `FLOAT`   | _syntax error_ | [`Decimal`][rust_decimal]  |
| `.456`             | _missing leading `0`_     |            |                |                            |
| `123.456e_10`      | _improper separator_      |            |                |                            |
| `123.e-10`         | _missing decimal `0`_     |            |                |                            |


Warning &ndash; No Implicit Type Conversions
--------------------------------------------

Unlike most C-like languages, Rhai does _not_ provide implicit type conversions between different
numeric types.

For example, a `u8` is never implicitly converted to `i64` when used as a parameter in a function
call or as a comparison operand.  `f32` is never implicitly converted to `f64`.

This is exactly the same as Rust where all numeric types are distinct.  Rhai is written in Rust afterall.

```admonish warning.small

Integer variables pushed inside a custom [`Scope`] must be the correct type.

It is extremely easy to mess up numeric types since the Rust default integer type is `i32` while for
Rhai it is `i64` (unless under [`only_i32`]).
```

```rust
use rhai::{Engine, Scope, INT};

let engine = Engine::new();

let mut scope = Scope::new();

scope.push("r", 42);            // 'r' is i32 (Rust default integer type)
scope.push("x", 42_u8);         // 'x' is u8
scope.push("y", 42_i64);        // 'y' is i64
scope.push("z", 42 as INT);     // 'z' is i64 (or i32 under 'only_i32')
scope.push("f", 42.0_f32);      // 'f' is f32

// Rhai integers are i64 (i32 under 'only_i32')
engine.eval::<String>("type_of(42)")? == "i64";

// false - i32 is never equal to i64
engine.eval_with_scope::<bool>(&mut scope, "r == 42")?;

// false - u8 is never equal to i64
engine.eval_with_scope::<bool>(&mut scope, "x == 42")?;

// true - i64 is equal to i64
engine.eval_with_scope::<bool>(&mut scope, "y == 42")?;

// true - INT is i64
engine.eval_with_scope::<bool>(&mut scope, "z == 42")?;

// false - f32 is never equal to f64
engine.eval_with_scope::<bool>(&mut scope, "f == 42.0")?;
```


Floating-Point vs. Decimal
--------------------------

~~~admonish tip.side.wide "Tip: `no_float` + `decimal`"

When both [`no_float`] and [`decimal`] features are turned on, [`Decimal`][rust_decimal] _replaces_
the standard floating-point type.

Floating-point number literals in scripts parse to [`Decimal`][rust_decimal] values.
~~~

[`Decimal`][rust_decimal] (enabled via the [`decimal`] feature) represents a fixed-precision
floating-point number which is popular with financial calculations and other usage scenarios where
round-off errors are not acceptable.

[`Decimal`][rust_decimal] takes up more space (16 bytes) than a standard `FLOAT` (4-8 bytes) and is
much slower in calculations due to the lack of CPU hardware support. Use it only when necessary.

For most situations, the standard floating-point number type `FLOAT` (`f64` or `f32` with
[`f32_float`]) is enough and is faster than [`Decimal`][rust_decimal].

It is possible to use both `FLOAT` and [`Decimal`][rust_decimal] together with just the [`decimal`] feature
&ndash; use [`parse_decimal`] or [`to_decimal`] to create a [`Decimal`][rust_decimal] value.


# object-maps-missing-prop.md
Non-Existent Property Handling for Object Maps
==============================================

{{#include ../links.md}}

[`Engine::on_map_missing_property`]: https://docs.rs/rhai/{{version}}/rhai/struct.Engine.html#method.on_map_missing_property
[`Target`]: https://docs.rs/rhai/latest/rhai/enum.Target.html


~~~admonish warning.small "Requires `internals`"

This is an advanced feature that requires the [`internals`] feature to be enabled.
~~~

Normally, when a property is accessed from an [object map] that does not exist, [`()`] is returned.
Via [`Engine:: set_fail_on_invalid_map_property`][options], it is possible to make this an error
instead.

Other than that, it is possible to completely control this behavior via a special callback function
registered into an [`Engine`] via `on_map_missing_property`.

Using this callback, for instance, it is simple to instruct Rhai to create a new property in the
[object map] on the fly, possibly with a default value, when a non-existent property is accessed.


Function Signature
------------------

The function signature passed to [`Engine::on_map_missing_property`] takes the following form.

> ```rust
> Fn(map: &mut Map, prop: &str, context: EvalContext) -> Result<Target, Box<EvalAltResult>>
> ```

where:

| Parameter |           Type           | Description                         |
| --------- | :----------------------: | ----------------------------------- |
| `map`     | [`&mut Map`][object map] | the [object map] being accessed     |
| `prop`    |          `&str`          | name of the property being accessed |
| `context` |     [`EvalContext`]      | the current _evaluation context_    |

### Return value

The return value is `Result<Target, Box<EvalAltResult>>`.

[`Target`] is an advanced type, available only under the [`internals`] feature, that represents a
_reference_ to a [`Dynamic`] value.

It can be used to point to a particular value within the [object map].


Example
-------

```rust
engine.on_map_missing_property(|map, prop, context| {
    match prop {
        "x" => {
            // The object-map can be modified in place
            map.insert("y".into(), (42_i64).into());

            // Return a mutable reference to an element
            let value_ref = map.get_mut("y").unwrap();
            Ok(value_ref.into())
        }
        "z" => {
            // Return a temporary value (not a reference)
            let value = Dynamic::from(100_i64);
            Ok(value.into())
        }
        // Return the standard property-not-found error
        _ => Err(EvalAltResult::ErrorPropertyNotFound(
                prop.to_string(), Position::NONE
             ).into()),
    }
});
```


# object-maps-oop.md
Special Support for OOP via Object Maps
=======================================

{{#include ../links.md}}

```admonish info.side "See also"

See the pattern on [_Simulating Object-Oriented Programming_][OOP] for more details.
```

[Object maps] can be used to simulate [object-oriented programming (OOP)][OOP] by storing data
as properties and methods as properties holding [function pointers].

If an [object map]'s property holds a [function pointer], the property can simply be called like
a normal method in method-call syntax.

This is a _short-hand_ to avoid the more verbose syntax of using the `call` function keyword.

When a property holding a [function pointer] or a [closure] is called like a method, it is replaced
as a method call on the [object map] itself.

```rust
let obj = #{
                data: 40,
                action: || this.data += x    // 'action' holds a closure
           };

obj.action(2);                               // calls the function pointer with 'this' bound to 'obj'

obj.call(obj.action, 2);                     // <- the above de-sugars to this

obj.data == 42;

// To achieve the above with normal function pointer call will fail.

fn do_action(map, x) { map.data += x; }      // 'map' is a copy

obj.action = do_action;                      // <- de-sugars to 'Fn("do_action")'

obj.action.call(obj, 2);                     // a copy of 'obj' is passed by value

obj.data == 42;                              // 'obj.data' is not changed
```


# object-maps.md
Object Maps
===========

{{#include ../links.md}}

```admonish tip.side "Safety"

Always limit the [maximum size of object maps].
```

Object maps are hash dictionaries. Properties are all [`Dynamic`] and can be freely added and retrieved.

The Rust type of a Rhai object map is `rhai::Map`.
Currently it is an alias to `BTreeMap<SmartString, Dynamic>`.

[`type_of()`] an object map returns `"map"`.

Object maps are disabled via the [`no_object`] feature.

~~~admonish tip "Tip: Object maps are _FAST_"

Normally, when [properties][getters/setters] are accessed, copies of the data values are made.
This is normally slow.

Object maps have special treatment &ndash; properties are accessed via _references_, meaning that
no copies of data values are made.

This makes object map access fast, especially when deep within a properties chain.

```rust
// 'obj' is a normal custom type
let x = obj.a.b.c.d;

// The above is equivalent to:
let a_value = obj.a;        // temp copy of 'a'
let b_value = a_value.b;    // temp copy of 'b'
let c_value = b_value.c;    // temp copy of 'c'
let d_value = c_value.d;    // temp copy of 'd'
let x = d_value;

// 'map' is an object map
let x = map.a.b.c.d;        // direct access to 'd'
                            // 'a', 'b' and 'c' are not copied

map.a.b.c.d = 42;           // directly modifies 'd' in 'a', 'b' and 'c'
                            // no copy of any property value is made

map.a.b.c.d.calc();         // directly calls 'calc' on 'd'
                            // no copy of any property value is made
```
~~~

~~~admonish question.small "TL;DR: Why `SmartString`?"

[`SmartString`] is used because most object map properties are short (at least shorter than 23 characters)
and ASCII-based, so they can usually be stored inline without incurring the cost of an allocation.
~~~

~~~admonish question.small "TL;DR: Why `BTreeMap` and not `HashMap`?"

The vast majority of object maps contain just a few properties.

`BTreeMap` performs significantly better than `HashMap` when the number of entries is small.
~~~


Literal Syntax
--------------

Object map literals are built within braces `#{` ... `}` with _name_`:`_value_ pairs separated by
commas `,`:

> `#{` _property_ `:` _value_`,` ... `,` _property_ `:` _value_ `}`
>
> `#{` _property_ `:` _value_`,` ... `,` _property_ `:` _value_ `,` `}`     `// trailing comma is OK`

The property _name_ can be a simple identifier following the same naming rules as [variables],
or a [string literal][literals] without interpolation.


Property Access Syntax
----------------------

### Dot notation

The _dot notation_ allows only property names that follow the same naming rules as [variables].

> _object_ `.` _property_

### Elvis notation

The [_Elvis notation_][elvis] is similar to the _dot notation_ except that it returns [`()`] if the object
itself is [`()`].

> `// returns () if object is ()`  
> _object_ `?.` _property_
>
> `// no action if object is ()`  
> _object_ `?.` _property_ `=` _value_ `;`

### Index notation

The _index notation_ allows setting/getting properties of arbitrary names (even the empty [string]).

> _object_ `[` _property_ `]`


Handle Non-Existent Properties
------------------------------

Trying to read a non-existent property returns [`()`] instead of causing an error.

This is similar to JavaScript where accessing a non-existent property returns `undefined`.

```rust
let map = #{ foo: 42 };

// Regular property access
let x = map.foo;            // x == 42

// Non-existent property
let x = map.bar;            // x == ()
```

```admonish tip.small "Tip: Force error"

It is possible to force Rhai to return an `EvalAltResult:: ErrorPropertyNotFound` via
[`Engine:: set_fail_on_invalid_map_property`][options].
```

```admonish tip.small "Advanced tip: Override standard behavior"

For fine-tuned control on what happens when a non-existent property is accessed,
see [_Non-Existent Property Handling for Object Maps_](object-maps-missing-prop.md).
```

### Check for property existence

Use the [`in`] operator to check whether a property exists in an object-map.

```rust
let map = #{ foo: 42 };

"foo" in map == true;

"bar" in map == false;
```

### Short-circuit non-existent property access

Use the [_Elvis operator_][elvis] (`?.`) to short-circuit further processing if the object is [`()`].

```rust
x.a.b.foo();        // <- error if 'x', 'x.a' or 'x.a.b' is ()

x.a.b = 42;         // <- error if 'x' or 'x.a' is ()

x?.a?.b?.foo();     // <- ok! returns () if 'x', 'x.a' or 'x.a.b' is ()

x?.a?.b = 42;       // <- ok even if 'x' or 'x.a' is ()
```

### Default property value

Using the [null-coalescing operator](logic.md#null-coalescing-operator) to give non-existent
properties default values.

```rust
let map = #{ foo: 42 };

// Regular property access
let x = map.foo;            // x == 42

// Non-existent property
let x = map.bar;            // x == ()

// Default value for property
let x = map.bar ?? 42;      // x == 42
```


Built-in Functions
------------------

The following methods (defined in the [`BasicMapPackage`][built-in packages] but excluded when using
a [raw `Engine`]) operate on object maps.

| Function                    | Parameter(s)                                                 | Description                                                                                                                                                                                                                                                   |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get`                       | property name                                                | gets a copy of the value of a certain property ([`()`] if the property does not exist); behavior is not affected by [`Engine::fail_on_invalid_map_property`][options]                                                                                         |
| `set`                       | <ol><li>property name</li><li>new element</li></ol>          | sets a certain property to a new value (property is added if not already exists)                                                                                                                                                                              |
| `len`                       | _none_                                                       | returns the number of properties                                                                                                                                                                                                                              |
| `is_empty`                  | _none_                                                       | returns `true` if the object map is empty                                                                                                                                                                                                                     |
| `clear`                     | _none_                                                       | empties the object map                                                                                                                                                                                                                                        |
| `remove`                    | property name                                                | removes a certain property and returns it ([`()`] if the property does not exist)                                                                                                                                                                             |
| `+=` operator, `mixin`      | second object map                                            | mixes in all the properties of the second object map to the first (values of properties with the same names replace the existing values)                                                                                                                      |
| `+` operator                | <ol><li>first object map</li><li>second object map</li></ol> | merges the first object map with the second                                                                                                                                                                                                                   |
| `==` operator               | <ol><li>first object map</li><li>second object map</li></ol> | are the two object maps the same (elements compared with the `==` operator, if defined)?                                                                                                                                                                      |
| `!=` operator               | <ol><li>first object map</li><li>second object map</li></ol> | are the two object maps different (elements compared with the `==` operator, if defined)?                                                                                                                                                                     |
| `fill_with`                 | second object map                                            | adds in all properties of the second object map that do not exist in the object map                                                                                                                                                                           |
| `contains`, [`in`] operator | property name                                                | does the object map contain a property of a particular name?                                                                                                                                                                                                  |
| `keys`                      | _none_                                                       | returns an [array] of all the property names (in random order), not available under [`no_index`]                                                                                                                                                              |
| `values`                    | _none_                                                       | returns an [array] of all the property values (in random order), not available under [`no_index`]                                                                                                                                                             |
| `drain`                     | [function pointer] to predicate (usually a [closure])        | removes all elements (returning them) that return `true` when called with the predicate function taking the following parameters:<ol><li>key</li><li>_(optional)_ object map element (if omitted, the object map element is bound to `this`)</li></ol>        |
| `retain`                    | [function pointer] to predicate (usually a [closure])        | removes all elements (returning them) that do not return `true` when called with the predicate function taking the following parameters:<ol><li>key</li><li>_(optional)_ object map element (if omitted, the object map element is bound to `this`)</li></ol> |
| `filter`                    | [function pointer] to predicate (usually a [closure])        | constructs a object map with all elements that return `true` when called with the predicate function taking the following parameters:<ol><li>key</li><li>_(optional)_ object map element (if omitted, the object map element is bound to `this`)</li></ol>    |
| `to_json`                   | _none_                                                       | returns a JSON representation of the object map ([`()`] is mapped to `null`, all other data types must be supported by JSON)                                                                                                                                  |


Examples
--------

```rust
let y = #{              // object map literal with 3 properties
    a: 1,
    bar: "hello",
    "baz!$@": 123.456,  // like JavaScript, you can use any string as property names...
    "": false,          // even the empty string!

    `hello`: 999,       // literal strings are also OK

    a: 42,              // <- syntax error: duplicated property name

    `a${2}`: 42,        // <- syntax error: property name cannot have string interpolation
};

y.a = 42;               // access via dot notation
y.a == 42;

y.baz!$@ = 42;          // <- syntax error: only proper variable names allowed in dot notation
y."baz!$@" = 42;        // <- syntax error: strings not allowed in dot notation
y["baz!$@"] = 42;       // access via index notation is OK

"baz!$@" in y == true;  // use 'in' to test if a property exists in the object map
("z" in y) == false;

ts.obj = y;             // object maps can be assigned completely (by value copy)
let foo = ts.list.a;
foo == 42;

let foo = #{ a:1, };    // trailing comma is OK

let foo = #{ a:1, b:2, c:3 }["a"];
let foo = #{ a:1, b:2, c:3 }.a;
foo == 1;

fn abc() {
    #{ a:1, b:2, c:3 }  // a function returning an object map
}

let foo = abc().b;
foo == 2;

let foo = y["a"];
foo == 42;

y.contains("a") == true;
y.contains("xyz") == false;

y.xyz == ();            // a non-existent property returns '()'
y["xyz"] == ();

y.len == ();            // an object map has no property getter function
y.len() == 3;           // method calls are OK

y.remove("a") == 1;     // remove property

y.len() == 2;
y.contains("a") == false;

for name in y.keys() {  // get an array of all the property names via 'keys'
    print(name);
}

for val in y.values() { // get an array of all the property values via 'values'
    print(val);
}

y.clear();              // empty the object map

y.len() == 0;
```


No Support for Property Getters
-------------------------------

In order not to affect the speed of accessing properties in an object map, new
[property getters][getters/setters] cannot be registered because they conflict with the syntax of
property access.

A [property getter][getters/setters] function registered via `Engine::register_get`, for example,
for a `Map` will never be found &ndash; instead, the property will be looked up in the object map.

Properties should be registered as _methods_ instead:

```rust
map.len                 // access property 'len', returns '()' if not found

map.len()               // 'len' method - returns the number of properties

map.keys                // access property 'keys', returns '()' if not found

map.keys()              // 'keys' method - returns array of all property names

map.values              // access property 'values', returns '()' if not found

map.values()            // 'values' method - returns array of all property values
```


# overload.md
Function Overloading
====================

{{#include ../links.md}}

[Functions] defined in script can be _overloaded_ by _arity_ (i.e. they are resolved purely upon the
function's _name_ and _number_ of parameters, but not parameter _types_ since all parameters are the
same type &ndash; [`Dynamic`]).

New definitions _overwrite_ previous definitions of the same name and number of parameters.

```js
fn foo(x, y, z) {
    print(`Three!!! ${x}, ${y}, ${z}`);
}
fn foo(x) {
    print(`One! ${x}`);
}
fn foo(x, y) {
    print(`Two! ${x}, ${y}`);
}
fn foo() {
    print("None.");
}
fn foo(x) {     // <- overwrites previous definition
    print(`HA! NEW ONE! ${x}`);
}

foo(1,2,3);     // prints "Three!!! 1,2,3"

foo(42);        // prints "HA! NEW ONE! 42"

foo(1,2);       // prints "Two!! 1,2"

foo();          // prints "None."
```


# print-debug.md
`print` and `debug`
===================

{{#include ../links.md}}

[`Engine::on_print`]: https://docs.rs/rhai/{{version}}/rhai/struct.Engine.html#method.on_print
[`Engine::on_debug`]: https://docs.rs/rhai/{{version}}/rhai/struct.Engine.html#method.on_debug


The `print` and `debug` functions default to printing to `stdout`, with `debug` using standard debug formatting.

```js
print("hello");         // prints "hello" to stdout

print(1 + 2 + 3);       // prints "6" to stdout

let x = 42;

print(`hello${x}`);     // prints "hello42" to stdout

debug("world!");        // prints "world!" to stdout using debug formatting
```


Override `print` and `debug` with Callback Functions
----------------------------------------------------

When embedding Rhai into an application, it is usually necessary to trap `print` and `debug` output
(for logging into a tracking log, for example) with the [`Engine::on_print`] and [`Engine::on_debug`] methods.

```rust
// Any function or closure that takes an '&str' argument can be used to override 'print'.
engine.on_print(|x| println!("hello: {x}"));

// Any function or closure that takes a '&str', an 'Option<&str>' and a 'Position' argument
// can be used to override 'debug'.
engine.on_debug(|x, src, pos| {
    let src = src.unwrap_or("unknown");
    println!("DEBUG of {src} at {pos:?}: {s}")
});

// Example: quick-'n-dirty logging
let logbook = Arc::new(RwLock::new(Vec::<String>::new()));

// Redirect print/debug output to 'log'
let log = logbook.clone();
engine.on_print(move |s| {
    let entry = format!("entry: {}", s);
    log.write().unwrap().push(entry);
});

let log = logbook.clone();
engine.on_debug(move |s, src, pos| {
    let src = src.unwrap_or("unknown");
    let entry = format!("DEBUG of {src} at {pos:?}: {s}");
    log.write().unwrap().push(entry);
});

// Evaluate script
engine.run(script)?;

// 'logbook' captures all the 'print' and 'debug' output
for entry in logbook.read().unwrap().iter() {
    println!("{entry}");
}
```


`on_debug` Callback Signature
-----------------------------

The function signature passed to [`Engine::on_debug]` takes the following form.

> ```rust
> Fn(text: &str, source: Option<&str>, pos: Position)
> ```

where:

| Parameter |      Type      | Description                                                     |
| --------- | :------------: | --------------------------------------------------------------- |
| `text`    |     `&str`     | text to display                                                 |
| `source`  | `Option<&str>` | source of the current evaluation, if any                        |
| `pos`     |   `Position`   | position (line number and character offset) of the `debug` call |

The _source_ of a script evaluation is any text string provided to an [`AST`] via `AST::set_source`.

```admonish tip.small

If a [module] is loaded via an [`import`] statement, then the _source_ of functions defined within
the module will be the module's _path_.
```


# ranges.md
Ranges
======

{{#include ../links.md}}


Syntax
------

Numeric ranges can be constructed by the `..` (exclusive) or `..=` (inclusive) operators.

### Exclusive range

> _start_ `..` _end_

An _exclusive_ range does not include the last (i.e. "end") value.

The Rust type of an exclusive range is `std::ops::Range<INT>`.

[`type_of()`] an exclusive range returns `"range"`.

### Inclusive range

> _start_ `..=` _end_

An _inclusive_ range includes the last (i.e. "end") value.

The Rust type of an inclusive range is `std::ops::RangeInclusive<INT>`.

[`type_of()`] an inclusive range returns `"range="`.


Usage Scenarios
---------------

Ranges are commonly used in the following scenarios.

| Scenario                   | Example                                 |
| -------------------------- | --------------------------------------- |
| [`for`] statements         | `for n in 0..100 { ... }`               |
| [`in`] expressions         | `if n in 0..100 { ... }`                |
| [`switch`] expressions     | `switch n { 0..100 => ... }`            |
| [Bit-fields] access        | `let x = n[2..6];`                      |
| Bits iteration             | `for bit in n.bits(2..=9) { ... }`      |
| [Array] range-based APIs   | `array.extract(2..8)`                   |
| [BLOB] range-based APIs    | `blob.parse_le_int(4..8)`               |
| [String] range-based APIs  | `string.sub_string(4..=12)`             |
| [Characters] iteration     | `for ch in string.bits(4..=12) { ... }` |
| [Custom types]             | `my_obj.action(3..=15, "foo");`         |


Use as Parameter Type
---------------------

Native Rust functions that take parameters of type `std::ops::Range<INT>` or
`std::ops::RangeInclusive<INT>`, when registered into an [`Engine`], accept ranges as arguments.

```admonish warning.small "Different types"

`..` (exclusive range) and `..=` (inclusive range) are _different_ types to Rhai
and they do not interoperate.

Two different versions of the same API must be registered to handle both range styles.
```

```rust
use std::ops::{Range, RangeInclusive};

/// The actual work function
fn do_work(obj: &mut TestStruct, from: i64, to: i64, inclusive: bool) {
    ...
}

let mut engine = Engine::new();

engine
    /// Version of API that accepts an exclusive range
    .register_fn("do_work", |obj: &mut TestStruct, range: Range<i64>|
        do_work(obj, range.start, range.end, false)
    )
    /// Version of API that accepts an inclusive range
    .register_fn("do_work", |obj: &mut TestStruct, range: RangeInclusive<i64>|
        do_work(obj, range.start(), range.end(), true)
    );

engine.run(
"
    let obj = new_ts();

    obj.do_work(0..12);         // use exclusive range

    obj.do_work(0..=11);        // use inclusive range
")?;
```

### Indexers Using Ranges

[Indexers] commonly use ranges as parameters.

```rust
use std::ops::{Range, RangeInclusive};

let mut engine = Engine::new();

engine
    /// Version of indexer that accepts an exclusive range
    .register_indexer_get_set(
        |obj: &mut TestStruct, range: Range<i64>| -> bool { ... },
        |obj: &mut TestStruct, range: Range<i64>, value: bool| { ... },
    )
    /// Version of indexer that accepts an inclusive range
    .register_indexer_get_set(
        |obj: &mut TestStruct, range: RangeInclusive<i64>| -> bool { ... },
        |obj: &mut TestStruct, range: RangeInclusive<i64>, value: bool| { ... },
    );

engine.run(
"
    let obj = new_ts();

    let x = obj[0..12];         // use exclusive range

    obj[0..=11] = !x;           // use inclusive range
")?;
```

Built-in Functions
------------------

The following methods (mostly defined in the [`BasicIteratorPackage`][built-in packages] but
excluded when using a [raw `Engine`]) operate on ranges.

| Function                           |  Parameter(s)   | Description                                   |
| ---------------------------------- | :-------------: | --------------------------------------------- |
| `start` method and property        |                 | beginning of the range                        |
| `end` method and property          |                 | end of the range                              |
| `contains`, [`in`] operator        | number to check | does this range contain the specified number? |
| `is_empty` method and property     |                 | returns `true` if the range contains no items |
| `is_inclusive` method and property |                 | is the range inclusive?                       |
| `is_exclusive` method and property |                 | is the range exclusive?                       |


TL;DR
-----

```admonish question "What happened to the _open-ended_ ranges?"

Rust has _open-ended_ ranges, such as `start..`, `..end` and `..=end`.  They are not available in Rhai.

They are not needed because Rhai can [overload][function overloading] functions.

Typically, an API accepting ranges as parameters would have equivalent versions that accept a
starting position and a length (the standard `start + len` pair), as well as a versions that accept
only the starting position (the length assuming to the end).

In fact, usually all versions redirect to a call to one single version.

For example, a naive implementation of the `extract` method for [arrays] (without any error handling)
would look like:

~~~rust
use std::ops::{Range, RangeInclusive};

// Version with exclusive range
#[rhai_fn(name = "extract", pure)]
pub fn extract_range(array: &mut Array, range: Range<i64>) -> Array {
    array[range].to_vec()
}
// Version with inclusive range
#[rhai_fn(name = "extract", pure)]
pub fn extract_range2(array: &mut Array, range: RangeInclusive<i64>) -> Array {
    extract_range(array, range.start()..range.end() + 1)
}
// Version with start
#[rhai_fn(name = "extract", pure)]
pub fn extract_to_end(array: &mut Array, start: i64) -> Array {
    extract_range(array, start..start + array.len())
}
// Version with start+len
#[rhai_fn(name = "extract", pure)]
pub fn extract(array: &mut Array, start: i64, len: i64) -> Array {
    extract_range(array, start..start + len)
}
~~~

Therefore, there should always be a function that can do what open-ended ranges are intended for.

The left-open form (i.e. `..end` and `..=end`) is trivially replaced by using zero as the starting
position with a length that corresponds to the end position (for `..end`).

The right-open form (i.e. `start..`) is trivially replaced by the version taking a single starting position.

~~~rust
let x = [1, 2, 3, 4, 5];

x.extract(0..3);    // normal range argument
                    // copies 'x' from positions 0-2

x.extract(2);       // copies 'x' from position 2 onwards
                    // equivalent to '2..'

x.extract(0, 2);    // copies 'x' from beginning for 2 items
                    // equivalent to '..2'
~~~
```


# return.md
Return Value
============

{{#include ../links.md}}

`return`
--------

The `return` statement is used to immediately stop evaluation and exist the current context
(typically a [function] call) yielding a _return value_.

```rust
return;             // equivalent to return ();

return 123 + 456;   // returns 579
```

A `return` statement at _global_ level stops the entire script evaluation,
the return value is taken as the result of the script evaluation.

A `return` statement inside a [function call][function] exits with a return value to the caller.


`exit`
------

Similar to the `return` statement, the `exit` _function_ is used to immediately stop evaluation,
but it does so regardless of where it is called from, even deep inside nested function calls.

```rust
fn foo() {
    exit(42);       // exit with result 42
}
fn bar() {
    foo();
}
fn baz() {
    bar();
}

let x = baz();      // exits with result 42

print(x);           // <- this is never run
```

The `exit` function is defined in the [`LanguageCorePackage`][built-in packages] but excluded when using a [raw `Engine`].

| Function | Parameter(s)              | Description                                                              |
| -------- | ------------------------- | ------------------------------------------------------------------------ |
| `exit`   | result value _(optional)_ | immediately terminate script evaluation (default result value is [`()`]) |


# shadow.md
Variable Shadowing
==================

{{#include ../links.md}}

In Rhai, new [variables] automatically _shadow_ existing ones of the same name.  There is no error.

This behavior is consistent with Rust.

```rust
let x = 42;
let y = 123;

print(x);           // prints 42

let x = 88;         // <- 'x' is shadowed here

// At this point, it is no longer possible to access the
// original 'x' on the first line...

print(x);           // prints 88

let x = 0;          // <- 'x' is shadowed again

// At this point, it is no longer possible to access both
// previously-defined 'x'...

print(x);           // prints 0

{
    let x = 999;    // <- 'x' is shadowed in a block
    
    print(x);       // prints 999
}

print(x);           // prints 0 - shadowing within the block goes away

print(y);           // prints 123 - 'y' is not shadowed
```


~~~admonish tip "Tip: Disable shadowing"

Set [`Engine::set_allow_shadowing`][options] to `false` to turn [variables] shadowing off.

```rust
let x = 42;

let x = 123;        // <- syntax error: variable 'x' already defined
                    //    when variables shadowing is disallowed
```
~~~


# statement-expression.md
Statement Expression
====================

{{#include ../links.md}}

```admonish warning.side "Differs from Rust"

This is different from Rust where, if the last statement is terminated by a semicolon, the block's
return value defaults to `()`.
```

Like Rust, a statement can be used anywhere where an _expression_ is expected.

These are called, for lack of a more creative name, "statement expressions."

The _last_ statement of a statements block is _always_ the block's return value when used as a statement,
_regardless_ of whether it is terminated by a semicolon or not.

If the last statement has no return value (e.g. variable definitions, assignments) then it is
assumed to be [`()`].

```rust
let x = {
    let foo = calc_something();
    let bar = foo + baz;
    bar.further_processing();       // <- this is the return value
};                                  // <- semicolon is needed here...

// The above is equivalent to:
let result;
{
    let foo = calc_something();
    let bar = foo + baz;
    result = bar.further_processing();
}
let x = result;

// Statement expressions can be inserted inside normal expressions
// to avoid duplicated calculations
let x = foo(bar) + { let v = calc(); process(v, v.len, v.abs) } + baz;

// The above is equivalent to:
let foo_result = foo(bar);
let calc_result;
{
    let v = calc();
    result = process(v, v.len, v.abs);  // <- avoid calculating 'v'
}
let x = foo_result + calc_result + baz;

// Statement expressions are also useful as function call arguments
// when side effects are desired
do_work(x, y, { let z = foo(x, y); print(z); z });
           // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
           //       statement expression
```

Statement expressions can be disabled via [`Engine::set_allow_statement_expression`][options].


# statements.md
Statements
==========

{{#include ../links.md}}


Statements are terminated by semicolons `;` and they are mandatory,
except for the _last_ statement in a _block_ (enclosed by `{` ... `}` pairs) where it can be omitted.

Semicolons can also be omitted for statement types that always end in a block &ndash; for example
the [`if`], [`while`], [`for`],  [`loop`] and [`switch`] statements.

```rust
let a = 42;             // normal assignment statement
let a = foo(42);        // normal function call statement
foo < 42;               // normal expression as statement

let a = { 40 + 2 };     // 'a' is set to the value of the statements block, which is the value of the last statement
//              ^ the last statement does not require a terminating semicolon (but also works with it)
//                ^ semicolon required here to terminate the 'let' statement
//                  it is a syntax error without it, even though it ends with '}'
//                  that is because the 'let' statement doesn't end in a block

if foo { a = 42 }
//               ^ no need to terminate an if-statement with a semicolon
//                 that is because the 'if' statement ends in a block

4 * 10 + 2              // a statement which is just one expression - no ending semicolon is OK
                        // because it is the last statement of the whole block
```


Statements Block
----------------

### Syntax

Statements blocks in Rhai are formed by enclosing zero or more statements within braces `{`...`}`.

> `{` _statement_`;` _statement_`;` ... _statement_ `}`
>
> `{` _statement_`;` _statement_`;` ... _statement_`;` `}`      `// trailing semi-colon is optional`

### Closed scope

A statements block forms a _closed_ scope.

Any [variable] and/or [constant] defined within the block are removed outside the block, so are
[modules] [imported][`import`] within the block.

```rust
let x = 42;
let y = 18;

{
    import "hello" as h;
    const HELLO = 99;
    let y = 0;

    h::greet();         // ok

    print(y + HELLO);   // prints 99 (y is zero)

        :    
        :    
}                       // <- 'HELLO' and 'y' go away here...

print(x + y);           // prints 60 (y is still 18)

print(HELLO);           // <- error: 'HELLO' not found

h::greet();             // <- error: module 'h' not found
```


# string-fn.md
Standard String Functions
=========================

{{#include ../links.md}}


The following standard methods (mostly defined in the [`MoreStringPackage`][built-in packages] but
excluded when using a [raw `Engine`]) operate on [strings] (and possibly characters).

| Function                                           | Parameter(s)                                                                                                                                    | Description                                                                                                                                                  |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `len` method and property                          | _none_                                                                                                                                          | returns the number of characters (**not** number of bytes) in the string                                                                                     |
| `bytes` method and property                        | _none_                                                                                                                                          | returns the number of bytes making up the UTF-8 string; for strings containing only ASCII characters, this is much faster than `len`                         |
| `is_empty` method and property                     | _none_                                                                                                                                          | returns `true` if the string is empty                                                                                                                        |
| `to_blob`<br/>(not available under [`no_index`])   | _none_                                                                                                                                          | converts the string into an UTF-8 encoded byte-stream and returns it as a [BLOB].                                                                            |
| `to_chars`<br/>(not available under [`no_index`])  | _none_                                                                                                                                          | splits the string by individual characters, returning them as an [array]                                                                                     |
| `get`                                              | position, counting from end if < 0                                                                                                              | gets the character at a certain position ([`()`] if the position is not valid)                                                                               |
| `set`                                              | <ol><li>position, counting from end if < 0</li><li>new character</li></ol>                                                                      | sets a certain position to a new character (no effect if the position is not valid)                                                                          |
| `pad`                                              | <ol><li>target length</li><li>character/string to pad</li></ol>                                                                                 | pads the string with a character or a string to at least a specified length                                                                                  |
| `append`, `+=` operator                            | item to append                                                                                                                                  | adds the display text of an item to the end of the string                                                                                                    |
| `remove`                                           | character/string to remove                                                                                                                      | removes a character or a string from the string                                                                                                              |
| `pop`                                              | _(optional)_ number of characters to remove, none if ≤ 0, entire string if ≥ length                                                             | removes the last character (if no parameter) and returns it ([`()`] if empty); otherwise, removes the last number of characters and returns them as a string |
| `clear`                                            | _none_                                                                                                                                          | empties the string                                                                                                                                           |
| `truncate`                                         | target length                                                                                                                                   | cuts off the string at exactly a specified number of characters                                                                                              |
| `to_upper`                                         | _none_                                                                                                                                          | converts the string/character into upper-case as a new string/character and returns it                                                                       |
| `to_lower`                                         | _none_                                                                                                                                          | converts the string/character into lower-case as a new string/character and returns it                                                                       |
| `make_upper`                                       | _none_                                                                                                                                          | converts the string/character into upper-case                                                                                                                |
| `make_lower`                                       | _none_                                                                                                                                          | converts the string/character into lower-case                                                                                                                |
| `trim`                                             | _none_                                                                                                                                          | trims the string of whitespace at the beginning and end                                                                                                      |
| `contains`                                         | character/sub-string to search for                                                                                                              | checks if a certain character or sub-string occurs in the string                                                                                             |
| `starts_with`                                      | string                                                                                                                                          | returns `true` if the string starts with a certain string                                                                                                    |
| `ends_with`                                        | string                                                                                                                                          | returns `true` if the string ends with a certain string                                                                                                      |
| `min`                                              | <ol><li>first character/string</li><li>second character/string</li><ol>                                                                         | returns the smaller of two characters/strings                                                                                                                |
| `max`                                              | <ol><li>first character/string</li><li>second character/string</li><ol>                                                                         | returns the larger of two characters/strings                                                                                                                 |
| `index_of`                                         | <ol><li>character/sub-string to search for</li><li>_(optional)_ start position, counting from end if < 0, end if ≥ length</li></ol>             | returns the position that a certain character or sub-string occurs in the string, or −1 if not found                                                         |
| `sub_string`                                       | <ol><li>start position, counting from end if < 0</li><li>_(optional)_ number of characters to extract, none if ≤ 0, to end if omitted</li></ol> | extracts a sub-string                                                                                                                                        |
| `sub_string`                                       | [range] of characters to extract, from beginning if ≤ 0, to end if ≥ length                                                                     | extracts a sub-string                                                                                                                                        |
| `split`<br/>(not available under [`no_index`])     | _none_                                                                                                                                          | splits the string by whitespaces, returning an [array] of string segments                                                                                    |
| `split`<br/>(not available under [`no_index`])     | position to split at (in number of characters), counting from end if < 0, end if ≥ length                                                       | splits the string into two segments at the specified character position, returning an [array] of two string segments                                         |
| `split`<br/>(not available under [`no_index`])     | <ol><li>delimiter character/string</li><li>_(optional)_ maximum number of segments, 1 if < 1</li></ol>                                          | splits the string by the specified delimiter, returning an [array] of string segments                                                                        |
| `split_rev`<br/>(not available under [`no_index`]) | <ol><li>delimiter character/string</li><li>_(optional)_ maximum number of segments, 1 if < 1</li></ol>                                          | splits the string by the specified delimiter in reverse order, returning an [array] of string segments                                                       |
| `crop`                                             | <ol><li>start position, counting from end if < 0</li><li>_(optional)_ number of characters to retain, none if ≤ 0, to end if omitted</li></ol>  | retains only a portion of the string                                                                                                                         |
| `crop`                                             | [range] of characters to retain, from beginning if ≤ 0, to end if ≥ length                                                                      | retains only a portion of the string                                                                                                                         |
| `replace`                                          | <ol><li>target character/sub-string</li><li>replacement character/string</li></ol>                                                              | replaces a sub-string with another                                                                                                                           |
| `chars` method and property                        | <ol><li>_(optional)_ start position, counting from end if < 0</li><li>_(optional)_ number of characters to iterate, none if ≤ 0</li></ol>       | allows iteration of the characters inside the string                                                                                                         |

Beware that functions that involve indexing into a [string] to get at individual [characters],
e.g. `sub_string`, require walking through the entire UTF-8 encoded bytes stream to extract
individual Unicode characters and counting them, which can be slow for long [strings].


Building Strings
----------------

[Strings] can be built from segments via the `+` operator.

| Operator           | Description                                                               |
| ------------------ | ------------------------------------------------------------------------- |
| [string] `+=` item | convert the item into a [string], then append it to the first [string]    |
| [string] `+` item  | convert the item into a [string], then concatenate them as a new [string] |
| item `+` [string]  | convert the item into a [string], then concatenate them as a new [string] |

```rust
let x = 42;

// Build string with '+'
let s = "The answer is: " + x + "!!!";

// Prints: "The answer is: 42!!!"
print(s);
```

### Standard Operators Between Strings and/or Characters

The following standard operators inter-operate between [strings] and/or [characters][strings].

When one (or both) of the operands is a [character], it is first converted into a one-character
[string] before running the operator.

| Operator  | Description                                   |
| --------- | --------------------------------------------- |
| `+`, `+=` | [character]/[string] concatenation            |
| `-`, `-=` | remove [character]/sub-[string] from [string] |
| `==`      | equals to                                     |
| `!=`      | not equals to                                 |
| `>`       | greater than                                  |
| `>=`      | greater than or equals to                     |
| `<`       | less than                                     |
| `<=`      | less than or equals to                        |

### Interop with BLOB's

For convenience, when a [BLOB] is appended to a [string], or vice versa, it is treated as a UTF-8
encoded byte stream and automatically first converted into the appropriate [string] value.

That is because it is rarely useful to append a [BLOB] into a string, but extremely useful to be
able to directly manipulate UTF-8 encoded text.

| Operator  | Description                                                                 |
| --------- | --------------------------------------------------------------------------- |
| `+`, `+=` | append a [BLOB] (as a UTF-8 encoded byte stream) to the end of the [string] |
| `+`       | concatenate a [BLOB] (as a UTF-8 encoded byte stream) with a [string]       |


Examples
--------

```rust
let full_name == " Bob C. Davis ";
full_name.len == 14;

full_name.trim();
full_name.len == 12;
full_name == "Bob C. Davis";

full_name.pad(15, '$');
full_name.len == 15;
full_name == "Bob C. Davis$$$";

let n = full_name.index_of('$');
n == 12;

full_name.index_of("$$", n + 1) == 13;

full_name.sub_string(n, 3) == "$$$";
full_name.sub_string(n..n+3) == "$$$";

full_name.truncate(6);
full_name.len == 6;
full_name == "Bob C.";

full_name.replace("Bob", "John");
full_name.len == 7;
full_name == "John C.";

full_name.contains('C') == true;
full_name.contains("John") == true;

full_name.crop(5);
full_name == "C.";

full_name.crop(0, 1);
full_name == "C";

full_name.clear();
full_name.len == 0;
```


# string-interp.md
Multi-Line Literal Strings
==========================

{{#include ../links.md}}

A [string] wrapped by a pair of back-tick (`` ` ``) characters is interpreted _literally_.

This means that every single character that lies between the two back-ticks is taken verbatim.

This include new-lines, whitespaces, escape characters etc.

```js
let x = `hello, world! "\t\x42"
  hello world again! 'x'
     this is the last time!!! `;

// The above is the same as:
let x = "hello, world! \"\\t\\x42\"\n  hello world again! 'x'\n     this is the last time!!! ";
```

If a back-tick (`` ` ``) appears at the _end_ of a line, then it is understood that the entire text
block starts from the _next_ line; the starting new-line character is stripped.

```js
let x = `
        hello, world! "\t\x42"
  hello world again! 'x'
     this is the last time!!!
`;

// The above is the same as:
let x = "        hello, world! \"\\t\\x42\"\n  hello world again! 'x'\n     this is the last time!!!\n";
```

To actually put a back-tick (`` ` ``) character inside a multi-line literal [string], use two
back-ticks together (i.e. ` `` `).

```js
let x = `I have a quote " as well as a back-tick `` here.`;

// The above is the same as:
let x = "I have a quote \" as well as a back-tick ` here.";
```


String Interpolation
====================

```admonish warning.side.wide "Only literal strings"

Interpolation is not supported for normal [string] or [character] literals.
```

Multi-line literal [strings] support _string interpolation_ wrapped in `${` ... `}`.

`${` ... `}` acts as a statements _block_ and can contain anything that is allowed within a
statements block, including another interpolated [string]!
The last result of the block is taken as the value for interpolation.

Rhai uses [`to_string`] to convert any value into a [string], then physically joins all the
sub-strings together.

For convenience, if any interpolated value is a [BLOB], however, it is automatically treated as a
UTF-8 encoded string.  That is because it is rarely useful to interpolate a [BLOB] into a [string],
but extremely useful to be able to directly manipulate UTF-8 encoded text.

To put `${` literally without interpolation, use `\${` instead.

```js
let x = 42;
let y = 123;

let s = `x = ${x} and y = ${y}.`;                   // <- interpolated string

let s = ("x = " + {x} + " and y = " + {y} + ".");   // <- de-sugars to this

s == "x = 42 and y = 123.";

let s = `
Undeniable logic:
1) Hello, ${let w = `${x} world`; if x > 1 { w += "s" } w}!
2) If ${y} > ${x} then it is ${y > x}!
3) \${x - y} is not interpolated because it is escaped!
`;

s == "Undeniable logic:\n1) Hello, 42 worlds!\n2) If 123 > 42 then it is true!\n3) ${x - y} is not interpolated because it is escaped!\n";

let blob = blob(3, 0x21);

print(blob);                            // prints [212121]

print(`Data: ${blob}`);                 // prints "Data: !!!"
                                        // BLOB is treated as UTF-8 encoded string

print(`Data: ${blob.to_string()}`);     // prints "Data: [212121]"
```


# strings-chars.md
Strings and Characters
======================

{{#include ../links.md}}

```admonish tip.side "Safety"

Always limit the [maximum length of strings].
```

String in Rhai contain any text sequence of valid Unicode characters.

Internally strings are stored in UTF-8 encoding.

[`type_of()`] a string returns `"string"`.


String and Character Literals
-----------------------------

String and character literals follow JavaScript-style syntax.

| Type                      |     Quotes      | Escapes? | Continuation? | Interpolation? |
| ------------------------- | :-------------: | :------: | :-----------: | :------------: |
| Normal string             |     `"..."`     |   yes    |   with `\`    |     **no**     |
| Raw string                | `#..#"..."#..#` |  **no**  |    **no**     |     **no**     |
| Multi-line literal string |   `` `...` ``   |  **no**  |    **no**     | with `${...}`  |
| Character                 |     `'...'`     |   yes    |    **no**     |     **no**     |

```admonish tip.small "Tip: Building strings"

Strings can be built up from other strings and types via the `+` operator
(provided by the [`MoreStringPackage`][built-in packages] but excluded when using a [raw `Engine`]).

This is particularly useful when printing output.
```


Standard Escape Sequences
-------------------------

~~~admonish tip.side "Tip: Character `to_int()`"

Use the `to_int` method to convert a Unicode character into its 32-bit Unicode encoding.
~~~

There is built-in support for Unicode (`\u`_xxxx_ or `\U`_xxxxxxxx_) and hex (`\x`_xx_) escape
sequences for normal strings and characters.

Hex sequences map to ASCII characters, while `\u` maps to 16-bit common Unicode code points and `\U`
maps the full, 32-bit extended Unicode code points.

Escape sequences are not supported for multi-line literal strings wrapped by back-ticks (`` ` ``).

| Escape sequence | Meaning                          |
| --------------- | -------------------------------- |
| `\\`            | back-slash (`\`)                 |
| `\t`            | tab                              |
| `\r`            | carriage-return (`CR`)           |
| `\n`            | line-feed (`LF`)                 |
| `\"` or `""`    | double-quote (`"`)               |
| `\'`            | single-quote (`'`)               |
| `\x`_xx_        | ASCII character in 2-digit hex   |
| `\u`_xxxx_      | Unicode character in 4-digit hex |
| `\U`_xxxxxxxx_  | Unicode character in 8-digit hex |


Line Continuation
-----------------

For a normal string wrapped by double-quotes (`"`), a back-slash (`\`) character at the end of a
line indicates that the string continues onto the next line _without any line-break_.

Whitespace up to the indentation of the opening double-quote is ignored in order to enable lining up
blocks of text.

Spaces are _not_ added, so to separate one line with the next with a space, put a space before the
ending back-slash (`\`) character.

```rust
let x = "hello, world!\
         hello world again! \
         this is the ""last"" time!!!";
// ^^^^^^ these whitespaces are ignored

// The above is the same as:
let x = "hello, world!hello world again! this is the \"last\" time!!!";
```

A string with continuation does not open up a new line.  To do so, a new-line character must be
manually inserted at the appropriate position.

```rust
let x = "hello, world!\n\
         hello world again!\n\
         this is the last time!!!";

// The above is the same as:
let x = "hello, world!\nhello world again!\nthis is the last time!!!";
```

~~~admonish warning.small "No ending quote before the line ends is a syntax error"

If the ending double-quote is omitted, it is a syntax error.

```rust
let x = "hello
# ";
//            ^ syntax error: unterminated string literal
```
~~~

```admonish question.small "Why not go multi-line?"

Technically speaking, there is no difficulty in allowing strings to run for multiple lines
_without_ the continuation back-slash.

Rhai forces you to manually mark a continuation with a back-slash because the ending quote is easy to omit.
Once it happens, the entire remainder of the script would become one giant, multi-line string.

This behavior is different from Rust, where string literals can run for multiple lines.
```


Raw Strings
-----------

A _raw string_ is any text enclosed by a pair of double-quotes (`"`), wrapped by hash (`#`) characters.

The number of hash (`#`) on each side must be the same.

Any text inside the double-quotes, as long as it is not a double-quote (`"`) followed by the same
number of hash (`#`) characters, is simply copied verbatim, _including control codes and/or
line-breaks_.

Raw strings are very useful for embedded regular expressions, file paths, and program code etc.

```rust
let x = #"Hello, I am a raw string! which means that I can contain
             line-breaks, \ slashes (not escapes), "quotes" and even # characters!"#

// Use more than one '#' if you happen to have '"###...' inside the string...

let x = ###"In Rhai, you can write ##"hello"## as a raw string."###;
//                                         ^^^ this is not the end of the raw string
```


Indexing
--------

Strings can be _indexed_ into to get access to any individual character.
This is similar to many modern languages but different from Rust.

### From beginning

Individual characters within a string can be accessed with zero-based, non-negative integer indices:

> _string_ `[` _index from 0 to (total number of characters − 1)_ `]`

### From end

A _negative_ index accesses a character in the string counting from the _end_, with −1 being the
_last_ character.

> _string_ `[` _index from −1 to −(total number of characters)_ `]`

```admonish warning.small "Character indexing can be SLOOOOOOOOW"

Internally, a Rhai string is still stored compactly as a Rust UTF-8 string in order to save memory.

Therefore, getting the character at a particular index involves walking through the entire UTF-8
encoded bytes stream to extract individual Unicode characters, counting them on the way.

Because of this, indexing can be a _slow_ procedure, especially for long strings.
Along the same lines, getting the _length_ of a string (which returns the number of characters, not
bytes) can also be slow.
```


Sub-Strings
-----------

Sub-strings, or _slices_ in some programming languages, are parts of strings.

In Rhai, a sub-string can be specified by indexing with a [range] of characters:

> _string_ `[` _first character (starting from zero)_ `..` _last character (exclusive)_ `]`
>
> _string_ `[` _first character (starting from zero)_ `..=` _last character (inclusive)_ `]`

Sub-string [ranges] always start from zero counting towards the end of the string.
Negative [ranges] are not supported.


Examples
--------

```js
let name = "Bob";
let middle_initial = 'C';
let last = "Davis";

let full_name = `${name} ${middle_initial}. ${last}`;
full_name == "Bob C. Davis";

// String building with different types
let age = 42;
let record = `${full_name}: age ${age}`;
record == "Bob C. Davis: age 42";

// Unlike Rust, Rhai strings can be indexed to get a character
// (disabled with 'no_index')
let c = record[4];
c == 'C';                               // single character

let slice = record[4..8];               // sub-string slice
slice == " C. D";

ts.s = record;                          // custom type properties can take strings

let c = ts.s[4];
c == 'C';

let c = ts.s[-4];                       // negative index counts from the end
c == 'e';

let c = "foo"[0];                       // indexing also works on string literals...
c == 'f';

let c = ("foo" + "bar")[5];             // ... and expressions returning strings
c == 'r';

let text = "hello, world!";
text[0] = 'H';                          // modify a single character
text == "Hello, world!";

text[7..=11] = "Earth";                 // modify a sub-string slice
text == "Hello, Earth!";

// Escape sequences in strings
record += " \u2764\n";                  // escape sequence of '❤' in Unicode
record == "Bob C. Davis: age 42 ❤\n";  // '\n' = new-line

// Unlike Rust, Rhai strings can be directly modified character-by-character
// (disabled with 'no_index')
record[4] = '\x58'; // 0x58 = 'X'
record == "Bob X. Davis: age 42 ❤\n";

// Use 'in' to test if a substring (or character) exists in a string
"Davis" in record == true;
'X' in record == true;
'C' in record == false;

// Strings can be iterated with a 'for' statement, yielding characters
for ch in record {
    print(ch);
}
```


# switch-expression.md
Switch Expression
=================

{{#include ../links.md}}

Like [`if`], [`switch`] also works as an _expression_.

```admonish tip.small "Tip"

This means that a [`switch`] expression can appear anywhere a regular expression can,
e.g. as [function] call arguments.
```

~~~admonish tip.small "Tip: Disable `switch` expressions"

[`switch`] expressions can be disabled via [`Engine::set_allow_switch_expression`][options].
~~~

```js
let x = switch foo { 1 => true, _ => false };

func(switch foo {
    "hello" => 42,
    "world" => 123,
    _ => 0
});

// The above is somewhat equivalent to:

let x = if foo == 1 { true } else { false };

if foo == "hello" {
    func(42);
} else if foo == "world" {
    func(123);
} else {
    func(0);
}
```


# switch.md
Switch Statement
================

{{#include ../links.md}}

The `switch` statement allows matching on [literal] values, and it mostly follows Rust's `match` syntax.

```js
switch calc_secret_value(x) {
    1 => print("It's one!"),
    2 => {
        // A statements block instead of a one-line statement
        print("It's two!");
        print("Again!");
    }
    3 => print("Go!"),
    // A list of alternatives
    4 | 5 | 6 => print("Some small number!"),
    // _ is the default when no case matches. It must be the last case.
    _ => print(`Oops! Something's wrong: ${x}`)
}
```


Default Case
------------

A _default_ case (i.e. when no other cases match) can be specified with `_`.

```admonish warning.small "Must be last"

The default case must be the _last_ case in the `switch` statement.
```

```js
switch wrong_default {
    1 => 2,
    _ => 9,     // <- syntax error: default case not the last
    2 => 3,
    3 => 4,     // <- ending with extra comma is OK
}

switch wrong_default {
    1 => 2,
    2 => 3,
    3 => 4,
    _ => 8,     // <- syntax error: default case not the last
    _ => 9
}
```


Array and Object Map Literals Also Work
---------------------------------------

The `switch` expression can match against any _[literal]_, including [array] and [object map] [literals].

```js
// Match on arrays
switch [foo, bar, baz] {
    ["hello", 42, true] => ...,
    ["hello", 123, false] => ...,
    ["world", 1, true] => ...,
    _ => ...
}

// Match on object maps
switch map {
    #{ a: 1, b: 2, c: true } => ...,
    #{ a: 42, d: "hello" } => ...,
    _ => ...
}
```

```admonish tip.small "Tip: Working with enums"

Switching on [arrays] is very useful when working with Rust enums
(see [this section]({{rootUrl}}/patterns/enums.md) for more details).
```


Case Conditions
---------------

Similar to Rust, each case (except the default case at the end) can provide an optional condition
that must evaluate to `true` in order for the case to match.

All cases are checked in order, so an earlier case that matches will override all later cases.

```js
let result = switch calc_secret_value(x) {
    1 if some_external_condition(x, y, z) => 100,

    1 | 2 | 3 if x < foo => 200,    // <- all alternatives share the same condition
    
    2 if bar() => 999,

    2 => "two",                     // <- fallback value for 2

    2 => "dead code",               // <- this case is a duplicate and will never match
                                    //    because the previous case matches first

    5 if CONDITION => 123,          // <- value for 5 matching condition

    5 => "five",                    // <- fallback value for 5

    _ if CONDITION => 8888          // <- syntax error: default case cannot have condition
};
```

~~~admonish tip "Tip: Use with `type_of()`"

Case conditions, together with [`type_of()`], makes it extremely easy to work with
values which may be of several different types (like properties in a JSON object).

```js
switch value.type_of() {
    // if 'value' is a string...
    "string" if value.len() < 5 => ...,
    "string" => ...,

    // if 'value' is an array...
    "array" => ...,

    // if 'value' is an object map...
    "map" if value.prop == 42 => ...,
    "map" => ...,

    // if 'value' is a number...
    "i64" if value > 0 => ...,
    "i64" => ...,

    // anything else: probably an error...
    _ => ...
}
```
~~~


Range Cases
-----------

Because of their popularity, [literal] integer [ranges] can also be used as `switch` cases.

Numeric [ranges] are only searched when the `switch` value is itself a number (including
floating-point and [`Decimal`][rust_decimal]). They never match any other data types.

```admonish warning.small "Must come after numeric cases"

Range cases must come _after_ all numeric cases.
```

```js
let x = 42;

switch x {
    'x' => ...,             // no match: wrong data type

    1 => ...,               // <- specific numeric cases are checked first
    2 => ...,               // <- but these do not match

    0..50 if x > 45 => ..., // no match: condition is 'false'

    -10..20 => ...,         // no match: not in range

    0..50 => ...,           // <- MATCH!!!

    30..100 => ...,         // no match: even though it is within range,
                            // the previous case matches first

    42 => ...,              // <- syntax error: numeric cases cannot follow range cases
}
```

```admonish tip.small "Tip: Ranges can overlap"

When more then one [range] contain the `switch` value, the _first_ one with a fulfilled condition
(if any) is evaluated.

Numeric [range] cases are tried in the order that they appear in the original script.
```


Difference From `if`-`else if` Chain
------------------------------------

Although a `switch` expression looks _almost_ the same as an [`if`-`else if`][`if`] chain, there are
subtle differences between the two.

### Look-up Table vs `x == y`

A `switch` expression matches through _hashing_ via a look-up table. Therefore, matching is very
fast.  Walking down an [`if`-`else if`][`if`] chain is _much_ slower.

On the other hand, operators can be [overloaded][operator overloading] in Rhai, meaning that it is
possible to override the `==` operator for integers such that `x == y` returns a different result
from the built-in default.

`switch` expressions do _not_ use the `==` operator for comparison; instead, they _hash_ the data
values and jump directly to the correct statements via a pre-compiled look-up table.  This makes
matching extremely efficient, but it also means that [overloading][operator overloading] the `==`
operator will have no effect.

Therefore, in environments where it is desirable to [overload][operator overloading] the `==`
operator for [standard types] &ndash; though it is difficult to think of valid scenarios where you'd
want `1 == 1` to return something other than `true` &ndash; avoid using the `switch` expression.

### Efficiency

Because the `switch` expression works through a look-up table, it is very efficient even for _large_
number of cases; in fact, switching is an O(1) operation regardless of the size of the data and
number of cases to match.

A long [`if`-`else if`][`if`] chain becomes increasingly slower with each additional case because
essentially an O(n) _linear scan_ is performed.


# throw.md
Throw Exception on Error
========================

{{#include ../links.md}}

All [`Engine`] evaluation API methods return `Result<T, Box<rhai::EvalAltResult>>`
with `EvalAltResult` holding error information.

To deliberately return an error, use the `throw` keyword.

```js
if some_bad_condition_has_happened {
    throw error;    // 'throw' any value as the exception
}

throw;              // defaults to '()'
```

Exceptions thrown via `throw` in the script can be captured in Rust by matching
`EvalAltResult::ErrorRuntime(value, position)` with the exception value captured by `value`.

```rust
let result = engine.eval::<i64>(
"
    let x = 42;

    if x > 0 {
        throw x;
    }
").expect_err();

println!("{result}");       // prints "Runtime error: 42 (line 5, position 15)"
```


Catch a Thrown Exception
------------------------

It is possible to _catch_ an exception instead of having it abort the evaluation
of the entire script via the [`try` ... `catch`][`try`]
statement common to many C-like languages.

```js
fn code_that_throws() {
    throw 42;
}

try
{
    code_that_throws();
}
catch (err)         // 'err' captures the thrown exception value
{
    print(err);     // prints 42
}
```


# timestamps.md
Timestamps
==========

{{#include ../links.md}}

Timestamps are provided by the [`BasicTimePackage`][built-in packages] (excluded when using a [raw `Engine`])
via the `timestamp` function.

Timestamps are not available under [`no_time`] or [`no_std`].

The Rust type of a timestamp is `std::time::Instant` ([`instant::Instant`] in [WASM] builds).

[`type_of()`] a timestamp returns `"timestamp"`.


Built-in Functions
------------------

The following methods (defined in the [`BasicTimePackage`][built-in packages] but excluded when
using a [raw `Engine`]) operate on timestamps.

| Function                      | Parameter(s)                                                | Description                                                           |
| ----------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------- |
| `elapsed` method and property | _none_                                                      | returns the number of seconds since the timestamp                     |
| `+` operator                  | number of seconds to add                                    | returns a new timestamp with a specified number of seconds added      |
| `+=` operator                 | number of seconds to add                                    | adds a specified number of seconds to the timestamp                   |
| `-` operator                  | number of seconds to subtract                               | returns a new timestamp with a specified number of seconds subtracted |
| `-=` operator                 | number of seconds to subtract                               | subtracts a specified number of seconds from the timestamp            |
| `-` operator                  | <ol><li>later timestamp</li><li>earlier timestamp</li></ol> | returns the number of seconds between the two timestamps              |

The following methods are defined in the [`LanguageCorePackage`][built-in packages] but excluded
when using a [raw `Engine`].

| Function | Not available under | Parameter(s)               | Description                                                 |
| -------- | :-----------------: | -------------------------- | ----------------------------------------------------------- |
| `sleep`  |     [`no_std`]      | number of seconds to sleep | blocks the current thread for a specified number of seconds |


Examples
--------

```rust
let now = timestamp();

// Do some lengthy operation...

if now.elapsed > 30.0 {
    print("takes too long (over 30 seconds)!")
}
```


# try-catch.md
Catch Exceptions
================

{{#include ../links.md}}


When an [exception] is thrown via a [`throw`] statement, evaluation of the script halts and the
[`Engine`] returns with `EvalAltResult::ErrorRuntime` containing the exception value thrown.

It is possible, via the `try` ... `catch` statement, to _catch_ exceptions, optionally with an
_error variable_.

> `try` `{` ... `}` `catch` `{` ... `}`
>
> `try` `{` ... `}` `catch` `(` _error variable_ `)` `{` ... `}`

```js
// Catch an exception and capturing its value
try
{
    throw 42;
}
catch (err)         // 'err' captures the thrown exception value
{
    print(err);     // prints 42
}

// Catch an exception without capturing its value
try
{
    print(42/0);    // deliberate divide-by-zero exception
}
catch               // no error variable - exception value is discarded
{
    print("Ouch!");
}

// Exception in the 'catch' block
try
{
    print(42/0);    // throw divide-by-zero exception
}
catch
{
    print("You seem to be dividing by zero here...");

    throw "die";    // a 'throw' statement inside a 'catch' block
                    // throws a new exception
}
```


~~~admonish tip "Tip: Re-throw exception"

Like the `try` ... `catch` syntax in most languages, it is possible to _re-throw_ an exception
within the `catch` block simply by another [`throw`] statement without a value.

```js
try
{
    // Call something that will throw an exception...
    do_something_bad_that_throws();
}
catch
{
    print("Oooh! You've done something real bad!");

    throw;          // 'throw' without a value within a 'catch' block
                    // re-throws the original exception
}

```
~~~

```admonish success "Catchable exceptions"

Many script-oriented exceptions can be caught via `try` ... `catch`.

| Error type                                            |         Error value          |
| ----------------------------------------------------- | :--------------------------: |
| Runtime error thrown by a [`throw`] statement         | value in [`throw`] statement |
| Arithmetic error                                      |         [object map]         |
| [Variable] not found                                  |         [object map]         |
| [Function] not found                                  |         [object map]         |
| [Module] not found                                    |         [object map]         |
| Unbound `this`                                        |         [object map]         |
| Data type mismatch                                    |         [object map]         |
| Assignment to a calculated/[constant] value           |         [object map]         |
| [Array]/[string]/[bit-field] indexing out-of-bounds   |         [object map]         |
| Indexing with an inappropriate data type              |         [object map]         |
| Error in property access                              |         [object map]         |
| [`for`] statement on a type without a [type iterator] |         [object map]         |
| Data race detected                                    |         [object map]         |
| Other runtime error                                   |         [object map]         |

The error value in the `catch` clause is an [object map] containing information on the particular error,
including its type, line and character position (if any), and source etc.

When the [`no_object`] feature is turned on, however, the error value is a simple [string] description.
```

```admonish failure "Non-catchable exceptions"

Some exceptions _cannot_ be caught.

| Error type                                                              | Notes                             |
| ----------------------------------------------------------------------- | --------------------------------- |
| System error &ndash; e.g. script file not found                         | system errors are not recoverable |
| Syntax error during parsing                                             | invalid script                    |
| [Custom syntax] mismatch error                                          | incompatible [`Engine`] instance  |
| Script evaluation metrics exceeding [limits][safety]                    | [safety] protection               |
| Script evaluation manually [terminated]({{rootUrl}}/safety/progress.md) | [safety] protection               |
```


# type-of.md
`type_of()`
===========

{{#include ../links.md}}

The `type_of` function detects the actual type of a value.

This is useful because all [variables] are [`Dynamic`] in nature.

```js
// Use 'type_of()' to get the actual types of values
type_of('c') == "char";
type_of(42) == "i64";

let x = 123;
x.type_of() == "i64";       // method-call style is also OK
type_of(x) == "i64";

x = 99.999;
type_of(x) == "f64";

x = "hello";
if type_of(x) == "string" {
    do_something_first_with_string(x);
}

switch type_of(x) {
    "string" => do_something_with_string(x),
    "char" => do_something_with_char(x),
    "i64" => do_something_with_int(x),
    "f64" => do_something_with_float(x),
    "bool" => do_something_with_bool(x),
    _ => throw `I cannot work with ${type_of(x)}!!!`
}
```

```admonish info.small "Standard types"

See [here][standard types] for the `type_of` output of standard types.
```

```admonish info.small "Custom types"

`type_of()` a [custom type] returns:

* the friendly name, if registered via `Engine::register_type_with_name`

* the full Rust type path, if registered via `Engine::register_type`

~~~rust
struct TestStruct1;
struct TestStruct2;

engine
    // type_of(struct1) == "path::to::module::TestStruct1"
    .register_type::<TestStruct1>()
    // type_of(struct2) == "MyStruct"
    .register_type_with_name::<TestStruct2>("MyStruct");
~~~
```


# values-and-types.md
Values and Types
================

{{#include ../links.md}}

The following primitive types are supported natively.

| Category                                                                                                               | Equivalent Rust types                                                                               | [`type_of()`](type-of.md) | `to_string()`                   |
| ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------- | ------------------------------- |
| **System integer**                                                                                                     | `rhai::INT` (default `i64`, `i32` under [`only_i32`])                                               | `"i32"` or `"i64"`        | `"42"`, `"123"` etc.            |
| **Other integer number**                                                                                               | `u8`, `i8`, `u16`, `i16`, `u32`, `i32`, `u64`, `i64`                                                | `"i32"`, `"u64"` etc.     | `"42"`, `"123"` etc.            |
| **Integer numeric [range]**                                                                                            | `std::ops::Range<rhai::INT>`, `std::ops::RangeInclusive<rhai::INT>`                                 | `"range"`, `"range="`     | `"2..7"`, `"0..=15"` etc.       |
| **Floating-point number** (disabled with [`no_float`])                                                                 | `rhai::FLOAT` (default `f64`, `f32` under [`f32_float`])                                            | `"f32"` or `"f64"`        | `"123.4567"` etc.               |
| **Fixed precision decimal number** (requires [`decimal`])                                                              | [`rust_decimal::Decimal`][rust_decimal]                                                             | `"decimal"`               | `"42"`, `"123.4567"` etc.       |
| **Boolean value**                                                                                                      | `bool`                                                                                              | `"bool"`                  | `"true"` or `"false"`           |
| **Unicode character**                                                                                                  | `char`                                                                                              | `"char"`                  | `"A"`, `"x"` etc.               |
| **Immutable Unicode [string]**                                                                                         | [`rhai::ImmutableString`][`ImmutableString`] (`Rc<SmartString>`, `Arc<SmartString>` under [`sync`]) | `"string"`                | `"hello"` etc.                  |
| **[`Array`]** (disabled with [`no_index`])                                                                             | [`rhai::Array`][array] (`Vec<Dynamic>`)                                                             | `"array"`                 | `"[ 1, 2, 3 ]"` etc.            |
| **Byte array &ndash; [`BLOB`]** (disabled with [`no_index`])                                                           | [`rhai::Blob`][BLOB] (`Vec<u8>`)                                                                    | `"blob"`                  | `"[01020304abcd]"` etc.         |
| **[Object map]** (disabled with [`no_object`])                                                                         | [`rhai::Map`][object map] (`BTreeMap<SmartString, Dynamic>`)                                        | `"map"`                   | `"#{ "a": 1, "b": true }"` etc. |
| **[Timestamp]** (disabled with [`no_time`] or [`no_std`])                                                              | `std::time::Instant` ([`instant::Instant`] if [WASM] build)                                         | `"timestamp"`             | `"<timestamp>"`                 |
| **[Function pointer]**                                                                                                 | [`rhai::FnPtr`][function pointer]                                                                   | `"Fn"`                    | `"Fn(foo)"` etc.                |
| **Dynamic value** (i.e. can be anything)                                                                               | [`rhai::Dynamic`][`Dynamic`]                                                                        | _the actual type_         | _actual value_                  |
| **Shared value** (a reference-counted, shared [`Dynamic`] value, created via [closures], disabled with [`no_closure`]) |                                                                                                     | _the actual type_         | _actual value_                  |
| **Nothing/void/nil/null/Unit** (or whatever it is called)                                                              | `()`                                                                                                | `"()"`                    | `""` _(empty string)_           |


```admonish warning.small "No automatic type conversion for integers"

The various integer types are treated strictly _distinct_ by Rhai, meaning that
`i32` and `i64` and `u32` and `u8` are completely different.

They cannot even be added together or compared with each other.

Nor can a smaller integer type be up-casted to a larger integer type.

This is very similar to Rust.
```


Default Types
-------------

The default integer type is `i64`. If other integer types are not needed, it is possible to exclude
them and make a smaller build with the [`only_i64`] feature.

If only 32-bit integers are needed, enabling the [`only_i32`] feature will remove support for all
integer types other than `i32`, including `i64`.
This is useful on some 32-bit targets where using 64-bit integers incur a performance penalty.

~~~admonish danger.small "Warning: Default integer is `i64`"

Rhai's default integer type is `i64`, which is _DIFFERENT_ from Rust's `i32`.

It is very easy to unsuspectingly set an `i32` into Rhai, which _still works_ but will incur a significant
runtime performance hit since the [`Engine`] will treat `i32` as an opaque [custom type] (unless using the
[`only_i32`] feature).

`i64` is the default even on 32-bit systems.  To use `i32` on 32-bit systems requires the [`only_i32`] feature.
~~~

```admonish tip.small "Tip: Floating-point numbers"

If no floating-point is needed or supported, use the [`no_float`] feature to remove it.

Some applications require fixed-precision decimal numbers, which can be enabled via the [`decimal`] feature.
```

```admonish info.small "Immutable strings"

[Strings] in Rhai are _immutable_, meaning that they can be shared but not modified.

Internally, the [`ImmutableString`] type is a wrapper over `Rc<String>` or `Arc<String>` (depending on [`sync`]).

Any modification done to a Rhai string causes the [string] to be cloned and the modifications made to the copy.
```

```admonish tip.small "Tip: Convert to string"

The [`to_string`] function converts a standard type into a [string] for display purposes.

The [`to_debug`] function converts a standard type into a [string] in debug format.
```


# variables.md
Variables
=========

{{#include ../links.md}}


Valid Names
-----------

```admonish tip.side.wide "Tip: Unicode Standard Annex #31 identifiers"

The [`unicode-xid-ident`] feature expands the allowed characters for variable names to the set defined by
[Unicode Standard Annex #31](http://www.unicode.org/reports/tr31/).
```

Variables in Rhai follow normal C naming rules &ndash; must contain only ASCII letters, digits and underscores `_`.

| Character set | Description              |
| :-----------: | ------------------------ |
|  `A` ... `Z`  | Upper-case ASCII letters |
|  `a` ... `z`  | Lower-case ASCII letters |
|  `0` ... `9`  | Digit characters         |
|      `_`      | Underscore character     |

However, unlike Rust, a variable name must also contain at least one ASCII letter, and an ASCII
letter must come _before_ any digits. In other words, the first character that is not an underscore `_`
must be an ASCII letter and not a digit.

```admonish question.side.wide "Why this restriction?"

To reduce confusion (and subtle bugs) because, for instance, `_1` can easily be misread (or mistyped)
as `-1`.

Rhai is dynamic without type checking, so there is no compiler to catch these typos.
```

Therefore, some names acceptable to Rust, like `_`, `_42foo`, `_1` etc., are not valid in Rhai.

For example: `c3po` and `_r2d2_` are valid variable names, but `3abc` and `____49steps` are not.

Variable names are case _sensitive_.

Variable names also cannot be the same as a [keyword] (active or reserved).

```admonish warning.small "Avoid names longer than 11 letters on 32-Bit"

Rhai uses [`SmartString`] which avoids allocations unless a string is over its internal limit
(23 ASCII characters on 64-bit, but only 11 ASCII characters on 32-bit).

On 64-bit systems, _most_ variable names are shorter than 23 letters, so this is unlikely to become
an issue.

However, on 32-bit systems, take care to limit, where possible, variable names to within 11 letters.
This is particularly true for local variables inside a hot loop, where they are created and
destroyed in rapid succession.

~~~js
// The following is SLOW on 32-bit
for my_super_loop_variable in array {
    print(`Super! ${my_super_loop_variable}`);
}

// Suggested revision:
for loop_var in array {
    print(`Super! ${loop_var}`);
}
~~~
```


Declare a Variable
------------------

Variables are declared using the `let` keyword.

```admonish tip.small "Tip: No initial value"

Variables do not have to be given an initial value.
If none is provided, it defaults to [`()`].
```

```admonish warning.small "Variables are local"

A variable defined within a [statements block](statements.md) is _local_ to that block.
```

~~~admonish tip.small "Tip: `is_def_var`"

Use `is_def_var` to detect if a variable is defined.
~~~

```rust
let x;              // ok - value is '()'
let x = 3;          // ok
let _x = 42;        // ok
let x_ = 42;        // also ok
let _x_ = 42;       // still ok

let _ = 123;        // <- syntax error: illegal variable name
let _9 = 9;         // <- syntax error: illegal variable name

let x = 42;         // variable is 'x', lower case
let X = 123;        // variable is 'X', upper case

print(x);           // prints 42
print(X);           // prints 123

{
    let x = 999;    // local variable 'x' shadows the 'x' in parent block

    print(x);       // prints 999
}

print(x);           // prints 42 - the parent block's 'x' is not changed

let x = 0;          // new variable 'x' shadows the old 'x'

print(x);           // prints 0

is_def_var("x") == true;

is_def_var("_x") == true;

is_def_var("y") == false;
```


Use Before Definition
---------------------

By default, variables do not need to be defined before they are used.

If a variable accessed by a script is not defined previously within the same script, it is assumed
to be provided via an external custom [`Scope`] passed to the [`Engine`] via the
`Engine::XXX_with_scope` API.

```rust
let engine = Engine::new();

engine.run("print(answer)")?;       // <- error: variable 'answer' not found

// Create custom scope
let mut scope = Scope::new();

// Add variable to custom scope
scope.push("answer", 42_i64);

// Run with custom scope
engine.run_with_scope(&mut scope,
    "print(answer)"                 // <- prints 42
)?;
```

~~~admonish bug.small "No `Scope`"

If no [`Scope`] is used to evaluate the script (e.g. when using `Engine::run` instead of
`Engine::run_with_scope`), an undefined variable causes a runtime error when accessed.
~~~


Strict Variables Mode
---------------------

With [`Engine::set_strict_variables`][options], it is possible to turn on
[_Strict Variables_][strict variables] mode.

When [strict variables] mode is active, accessing a variable not previously defined within
the same script directly causes a parse error when compiling the script.

```rust
let x = 42;

print(x);           // prints 42

print(foo);         // <- parse error under strict variables mode:
                    //    variable 'foo' is undefined
```

```admonish tip.small

Turn on [strict variables] mode if no [`Scope`] is to be provided for script evaluation runs.
This way, variable access errors are caught during compile time instead of runtime.
```


# while.md
While Loop
==========

{{#include ../links.md}}

`while` loops follow C syntax.

Like C, `continue` can be used to skip to the next iteration, by-passing all following statements;
`break` can be used to break out of the loop unconditionally.

~~~admonish tip.small "Tip: Disable `while` loops"

`while` loops can be disabled via [`Engine::set_allow_looping`][options].
~~~

```rust
let x = 10;

while x > 0 {
    x -= 1;
    if x < 6 { continue; }  // skip to the next iteration
    print(x);
    if x == 5 { break; }    // break out of while loop
}
```


While Expression
----------------

Like Rust, `while` statements can also be used as _expressions_.

The `break` statement takes an optional expression that provides the return value.

The default return value of a `while` expression is [`()`].

~~~admonish tip.small "Tip: Disable all loop expressions"

Loop expressions can be disabled via [`Engine::set_allow_loop_expressions`][options].
~~~

```js
let x = 0;

// 'while' can be used just like an expression
let result = while x < 100 {
    if is_magic_number(x) {
        // if the 'while' loop breaks here, return a specific value
        break get_magic_result(x);
    }

    x += 1;

    // ... if the 'while' loop exits here, the return value is ()
};

if result == () {
    print("Magic number not found!");
} else {
    print(`Magic result = ${result}!`);
}
```
