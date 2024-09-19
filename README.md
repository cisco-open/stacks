<div align="center">
	<p><img src=".github/logo.png" width="200px"></p>
	<h1>Stacks for Terraform</h1>
	<p>The <a href="https://www.terraform.io/">Terraform</a> code pre-processor</p>
</div>


## What is Stacks for Terraform?

**Stacks** is a code pre-processor for Terraform. It implements a **sustainable scaling pattern**, **prevents drift** and **boilerplate**, all while **plugging into your already existing Terraform pipeline**.

Stacks was initially presented at [SREcon23 Americas](https://www.usenix.org/conference/srecon23americas/presentation/bejarano).

***Warning:** Stacks is under heavy development, many things may change.*


## What is a "stack"?

- A **stack** is a set of Terraform resources you want to deploy one or more times.
- Each instance of a stack is a **layer**. A stack has one or more layers, hence, the name "stacks".

### Example

```
vpc/
│
├── base/
│   ├── vpc.tf
│   └── subnets.tf
│
├── layers/
│   ├── production/
│   │   └── layer.tfvars
│   └── staging/
│       ├── layer.tfvars
│       └── vpn.tf
│
└── stack.tfvars
```

- This is an example stack called `vpc`.
- It contains a `base` folder, containing the common Terraform configuration scoped for all layers in this stack.
- It contains a `layers` folder with two layers, one called `production` and one called `staging`. Layer directories contain layer-specific Terraform configuration.
- Finally, it contains an optional `stack.tfvars` file, which defines variables global to all layers in the stack. These variables can be overriden at the layer level through a layer-specific `layer.tfvars`.


## How does Stacks work?

Stacks sits between you (the Terraform user) and Terraform. It's a **code pre-processor**.
Here's an overview of Stacks inner workings:

1. It takes your stack definitions (as shown above)
1. For each layer:
  1. Joins the `base` code with the layer-specific code
  1. Applies a number of transformations
  1. Injects some extra configuration
  1. Bundles it up for Terraform to plan/apply on it


## How to use Stacks?

First, install the package with `pip`:

```shell
pip install git+https://github.com/cisco-open/stacks
```

Next, configure your stack definitions. Here's an example:

```plain
your-terraform-repository/
│
├── environments/                 # see the `example` directory on how to set this up
│   ├── production/
│   │   ├── backend.tfvars
│   │   └── environment.tfvars
│   └── staging/
│
└── stacks/                       # put your stack definitions here
    └── vpc/                      # the `vpc` stack shown above
        ├── base/
        │   ├── vpc.tf
        │   └── subnets.tf
        ├── layers/
        │   ├── production/
        │   │   └── layer.tfvars
        │   └── staging/
        │       ├── layer.tfvars
        │       └── vpn.tf
        └── stack.tfvars
```

You can find [another example here](example/stacks/example) with all the appropriate file contents.

Then you need to run Stacks in the layer you want to apply:

```shell
cd stacks/vpc/layers/production
stacks preinit
cd stacks.out  # where the preinit output goes
terraform init
stacks postinit
```

Now you're ready to run any further `terraform` commands in the `stacks.out` directory.

***Note:** we recommend putting `stacks.out` in `.gitignore` to prevent it from being tracked by git.*
