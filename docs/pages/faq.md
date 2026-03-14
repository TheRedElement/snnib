# FAQ

## `Network Container` does not transform to a wireframe when hitting `Build SNN`
### Cause 1: Deleted `Geometry Nodes` group
* most likely you have deleted and re-generated the necessary `Geometry Nodes` group which leads to
    * `Network Container` still has the `Geometry Nodes` modifier attached but no `node tree` linked anymore
        * behaves as if no `Geometry Nodes` applied at all

#### Solution 1:
> delete all the `Geometry Nodes` modifiers and hit `Build SNN` again
#### Solution 2:
> copy the nodes from `SnnibNetworkContainer` into the associated `Geometry Nodes` modifier
