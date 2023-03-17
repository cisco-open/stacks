<div align="center">
	<p><img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIj4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2ZXJzaW9uPSIxLjEiIHdpZHRoPSIxODQwcHgiIGhlaWdodD0iMTI1MHB4IiB2aWV3Qm94PSItMC41IC0wLjUgMTg0MCAxMjUwIiBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjogcmdiKDI1NSwgMjU1LCAyNTUpOyI+PGRlZnMvPjxnPjxwYXRoIGQ9Ik0gOTE3LjUgMzUwIEwgMTgzNSA3OTcuNSBMIDkxNy41IDEyNDUgTCAwIDc5Ny41IFoiIGZpbGwtb3BhY2l0eT0iMC43IiBmaWxsPSIjZmI3YzMyIiBzdHJva2U9Im5vbmUiIHBvaW50ZXItZXZlbnRzPSJhbGwiLz48cGF0aCBkPSJNIDkxNy41IDE3NSBMIDE4MzUgNjIyLjUgTCA5MTcuNSAxMDcwIEwgMCA2MjIuNSBaIiBmaWxsLW9wYWNpdHk9IjAuNyIgZmlsbD0iI2ZiN2MzMiIgc3Ryb2tlPSJub25lIiBwb2ludGVyLWV2ZW50cz0iYWxsIi8+PHBhdGggZD0iTSA5MTcuNSAwIEwgMTgzNSA0NDcuNSBMIDkxNy41IDg5NSBMIDAgNDQ3LjUgWiIgZmlsbC1vcGFjaXR5PSIwLjciIGZpbGw9IiNmYjdjMzIiIHN0cm9rZT0ibm9uZSIgcG9pbnRlci1ldmVudHM9ImFsbCIvPjwvZz48L3N2Zz4=" width="100px"></p>
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

First, you need to put the Stacks code somewhere close to your stack definitions.
Here's an example (not necessarily what we recommend):

```
your-terraform-repository/
│
├── src/                          # the contents of the `src` directory
│   ├── helpers.py
│   ├── postinit.py
│   └── preinit.py
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

Then you need to run Stacks in the layer you want to apply:
```bash
cd stacks/vpc/layers/production
python3 ../../../../src/preinit.py
cd stacks.out  # where the preinit output goes
terraform init
python3 ../../../../../src/postinit.py
```

Now you're ready to run any further `terraform` commands in the `stacks.out` directory.

***Note:** we recommend putting `stacks.out` in `.gitignore` to prevent it from being tracked by git.*
