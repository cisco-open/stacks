<div align="center">
	<p><img src=".github/logo.png" width="200px"></p>
	<h1>Stacks for Terraform</h1>
	<p>The <a href="https://www.terraform.io/">Terraform</a> code pre-processor</p>
</div>


## What is Stacks?

**Stacks** is a [Terraform](https://www.terraform.io/) code pre-processor.
Its primary goal is to minimize your total Terraform codebase without giving up on coverage. To do more with less.

As a code pre-processor, Stacks receives your "input code" and returns "output code" for Terraform to consume.

Stacks was originally developed and continues to be maintained by the Infrastructure SRE team at [Cisco ThousandEyes](https://www.thousandeyes.com/).
It was initially presented and open-sourced at [SREcon23 Americas](https://www.usenix.org/conference/srecon23americas/presentation/bejarano).

You can read "Terraform" and "OpenTofu" interchangeably, Stacks works with both but we've chosen to go with "Terraform" for readability.

The ["I am starting from scratch" quick-start guide](<2.2. I am starting from scratch.md>) is a good introduction to Stacks and what it does.


## Documentation

1. About
    1. [Considerations before using](<docs/1.1. Considerations before using.md>)
    2. [Stacks vs. its alternatives](<docs/1.2. Stacks vs its alternatives.md>)

2. Quick-start guide
    1. [Installation instructions](<docs/2.1. Installation instructions.md>)
    2. [I am starting from scratch](<docs/2.2. I am starting from scratch.md>)
    3. [I am collaborating to an existing stack](<docs/2.3. I am collaborating to an existing stack.md>)
    4. [I am collaborating to Stacks itself](<docs/2.4. I am collaborating to Stacks itself.md>)

3. Reference
    1. Native features
        1. [Global Terraform code](<docs/3.1.1. Global Terraform code.md>)
        2. [Reusable root modules](<docs/3.1.2. Reusable root modules.md>)
        3. [Jinja templating for Terraform](<docs/3.1.3. Jinja templating for Terraform.md>)
        4. [Jinja templating for variables](<docs/3.1.4. Jinja templating for variables.md>)
        5. [Custom Jinja functions](<docs/3.1.5. Custom Jinja functions.md>)
        6. [Inline secret encryption](<docs/3.1.6. Inline secret encryption.md>)
        7. [Automatic variable initialization](<docs/3.1.7. Automatic variable initialization.md>)
    2. Features you can build with Stacks
        1. [Terraform state backend configuration](<docs/3.2.1. Terraform state backend configuration.md>)
        2. [Terraform provider generation](<docs/3.2.2. Terraform provider generation.md>)
        3. [Input validation](<docs/3.2.3. Input validation.md>)
    3. Command-line interface
        1. [`stacks render`](<docs/3.3.1. stacks render.md>)
        2. [`stacks terraform`](<docs/3.3.2. stacks terraform.md>)
        3. [`stacks diff`](<docs/3.3.3. stacks diff.md>)
        4. [`stacks encrypt`](<docs/3.3.4. stacks encrypt.md>)
        5. [`stacks decrypt`](<docs/3.3.5. stacks decrypt.md>)
        6. [`stacks surgery list`](<docs/3.3.6. stacks surgery list.md>)
        7. [`stacks surgery import`](<docs/3.3.7. stacks surgery import.md>)
        8. [`stacks surgery remove`](<docs/3.3.8. stacks surgery remove.md>)
        9. [`stacks surgery rename`](<docs/3.3.9. stacks surgery rename.md>)
        10. [`stacks surgery move`](<docs/3.3.10. stacks surgery move.md>)
        11. [`stacks surgery edit`](<docs/3.3.11. stacks surgery edit.md>)
        12. [`stacks version`](<docs/3.3.12. stacks version.md>)
    4. [Directory structure](<docs/3.4. Directory structure.md>)
    5. [Special variables](<docs/3.5. Special variables.md>)
