## How to work on a Web API

### Part 1: Basic Setup of a Web API
1. Read-up on the relevant spec.
2. Add `.webidl` file(s) in [this folder](https://github.com/servo/servo/tree/168f7ead152c679ba1e0b8cdddd89e66433b512b/components/script_bindings/webidls) for each interface that you want to implement. If one already exists, you want to add the missing parts to it. 
3. For each interface, this will generate a trait named `{interface_name}Methods`, 
   accessible via `use crate::dom::bindings::codegen::Bindings::{interface_name}Binding`. 
4. Use this trait by:
   - Adding a matching struct, using `#[dom_struct]`
   - Adding methods with `todo!` bodies. 
5. At this point, the struct can have only one member: `reflector_: Reflector,`
   - The struct should be documented with a link to its interface in the spec, 
   - The trait methods should each be documented with a link to their definition in the interface.
   - [Example result](https://github.com/servo/servo/pull/34844/commits/5c842527d89f9c715f27427913a8d5fc6b18d4c7).
5. Back in the spec, 
   - look for definitions of further members for your struct. 
   - These are usually referred to as "internal slots"([example](https://streams.spec.whatwg.org/#default-reader-internal-slots)), 
   or as something that is "associated" with the interface([example](https://html.spec.whatwg.org/#message-channels)). 
6. Read-up on [DOM interfaces](https://github.com/servo/servo/blob/4a5ff01e060293721d10289ec56dbd4c58a0969e/components/script/dom/mod.rs).
7. Using what you know, for each internal slot of the interface:
   - Add an appropriate member to the struct(s) added at 4.
   - If this requires defining other structs or enums, these should derive `JSTraceable` and `MallocSizeOf`([example](https://github.com/servo/servo/pull/34844/commits/7d73370b0c41a1b00f4b25b7e1b8bf9b67430708#diff-2e7f6e100fdbd73318de2dda9b3d3883700be9ebfd028d4412a207e93cb02892R53)).
   - All `JSTraceable` structs added above that contain members that must be rooted because they are either [JS values](https://github.com/servo/mozjs/blob/87cabf4e9ddf9fafe19713a3d6bc8c5e6105544c/mozjs/src/gc/collections.rs#L94) or [Dom Objects](https://github.com/servo/servo/blob/9887ad369d65eb362db21c778ae5f00aad74db6c/components/script/dom/bindings/root.rs#L5) should be marked with `#[cfg_attr(crown, crown::unrooted_must_root_lint::must_root)]`. [Example](https://github.com/gterzian/servo/blob/b7688fe916d105ae9023cd2429068f16ecba3574/components/script/dom/readablestreamdefaultcontroller.rs#L120), where the lint is needed due to the presence of a `JSVal`.
   - If such a struct is assigned to a variable, `impl js::gc::Rootable` for the and use `rooted!` to root the variable([example](https://github.com/servo/servo/pull/34844/commits/94867eec21e06d59c5479bdaa92ef422bc7b21f9)).
   - All of this can be changed later, so simply use your best judgement at this stage. 
   - Add methods for [construction](https://github.com/servo/servo/blob/4a5ff01e060293721d10289ec56dbd4c58a0969e/components/script/dom/mod.rs#L91)(not to be confused with a `Constructor` that is part of the Web API). 
   - [Example result](https://github.com/servo/servo/pull/34844/commits/7d73370b0c41a1b00f4b25b7e1b8bf9b67430708).

### Part 2: Writing a First Draft
1. For each methods of the bindings trait referred to at 3 in Part 1:
   - In general, follow the structure of the spec: if a method calls into another named algorithm, implement that named algorithm as a separate private method of your struct, that the trait methods calls into. If you later realize this private method can be used from other structs, make it `pub(crate)`. 
   - For each algorithm step in the spec:
       - Copy the line from the spec. 
       - Implement the spec in code(which may take more than one line, and might require additional commenting).
2. Note: there are certain things that are often needed to perform operation as part of an algorithm: 
   - `SafeJSContext`: can be obtained using `GlobalScope::get_cx()`.
   - `GlobalScope`: can be obtained using `self.global()` on a `dom_struct`, or `GlobalScope::from_safe_context`
   - `InRealm`: can be obtained as an argument to the generated trait method, using [this configuration file](https://github.com/servo/servo/blob/4a5ff01e060293721d10289ec56dbd4c58a0969e/components/script_bindings/codegen/Bindings.conf)
   - `CanGc`: same as for `InRealm`.
   -  It is best to access them as early as possible, say at the top of the trait method implementation, and to pass them down(as ref for `GlobalScope`) as arguments, in the order described above(with any other needed argument coming in between `&GlobalScope` and `InRealm`). 
2. This should give you a complete first draft. 

### Part 3: Running tests and fixing bugs
1. Now comes the time to identify which [WPT test](https://book.servo.org/hacking/testing.html) to run against your first draft. You can find them [here](https://github.com/servo/servo/tree/168f7ead152c679ba1e0b8cdddd89e66433b512b/tests/wpt).
    - This may require turning them on, using [this config](https://github.com/servo/servo/blob/168f7ead152c679ba1e0b8cdddd89e66433b512b/tests/wpt/include.ini).
 2. Test may fail because:
     - There is a bug in the code. These should be fixed. 
     - The test uses other APIs that aren't supported yet(usually `ERROR`). 
3. Bugs should be fixed. Copilot is of little help here. 
4. Expected failures can be marked as such, using the process described [here](https://book.servo.org/hacking/testing.html#updating-web-test-expectations).
5. This part is done when there are no unexpected test results left. 
6. On occasion, on the advice of a reviewer, you may file an issue and describe a failure that you cannot fix, mark the test as a failure, and leave it to a follow-up. 

### Part 4: Refactoring and asking for a final review
1. While you may ask for a review at any time if stuck, now is the time to take a last look at your code and decide if you want to refactor anything.
2. If you are satisfied, now is the time to ask for a final review. 
3. Congratulations, the new Web API you implemented should soon merge.