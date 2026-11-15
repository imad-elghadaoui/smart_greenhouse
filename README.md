# Smart Greenhouse

[![CI](https://github.com/imad-elghadaoui/smart_greenhouse/actions/workflows/ci.yml/badge.svg)](https://github.com/imad-elghadaoui/smart_greenhouse/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A ROS 2 workspace that simulates a smart greenhouse. Two sensor nodes publish
temperature and humidity, two controllers drive ventilation and irrigation with
hysteresis, and a monitoring layer records the readings and raises an alert when
the temperature becomes critical.

The stack targets ROS 2 Humble and is written in Python 3 with `rclpy`. Decision
logic lives in plain Python modules that are independent of the ROS 2 transport
layer, so it can be unit-tested without a running ROS graph.

## Features

- Temperature and humidity sensor nodes with configurable simulation
  parameters (set point, noise, valid range) and validation of every reading.
- Ventilation controller with hysteresis (on above 25 °C, off below 20 °C by
  default) and a manual override service.
- Irrigation controller driven by humidity with inverted hysteresis (on below
  40 %, off above 60 % by default) and a manual override service.
- Alert system that requests ventilation through the `/toggle_ventilation`
  service, rate-limited by a configurable cooldown.
- Data logger that prints samples and can append them to a CSV file.
- All thresholds, rates and bounds exposed as ROS 2 parameters.
- Launch file and default parameter file in a dedicated `greenhouse_bringup`
  package.

> The sensors currently publish **simulated** readings; there is no hardware
> driver in this repository. See [Known limitations](#known-limitations).

## Architecture

The workspace is split into focused packages with a single shared utility
package. Dependencies point in one direction, from the applications towards the
shared helpers.

```
                 greenhouse_bringup
                 (launch + config)
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
 greenhouse_sensors  greenhouse_control  greenhouse_monitor
        └───────────────┴───────────────┘
                        │
                        ▼
                greenhouse_common
              (runtime + validation)
```

| Package | Responsibility |
| --- | --- |
| `greenhouse_common` | Shared `run_node` lifecycle helper, reading validation and QoS profiles. |
| `greenhouse_sensors` | Simulated temperature and humidity acquisition. |
| `greenhouse_control` | Ventilation and irrigation actuation logic. |
| `greenhouse_monitor` | Data logging and temperature alerting. |
| `greenhouse_bringup` | Launch files and default parameters. |

Each application package keeps its decision logic in a module that has no ROS
dependency (`sensor_model.py`, `control_logic.py`, `monitoring_logic.py`,
`csv_recorder.py`), and a thin node module that wires that logic to topics and
services. This keeps the logic testable with plain `pytest`.

### Data flow

```
temperature_sensor ──/temperature──▶ ventilation_controller ──/ventilation_state
                                   ├▶ alert_system ──SetBool──▶ /toggle_ventilation
                                   └▶ data_logger

humidity_sensor ────/humidity─────▶ irrigation_controller ───/irrigation_state
                                   └▶ data_logger
```

## Repository layout

The main files and packages are:

```
smart_greenhouse/
├── .github/workflows/ci.yml      # lint and build-and-test jobs
├── .pre-commit-config.yaml       # local style hooks
├── requirements-dev.txt          # development tooling
└── src/
    ├── greenhouse_common/        # shared helpers (no nodes)
    ├── greenhouse_sensors/       # temperature and humidity nodes
    ├── greenhouse_control/       # ventilation and irrigation nodes
    ├── greenhouse_monitor/       # data logger and alert system nodes
    └── greenhouse_bringup/       # launch file and default parameters
```

Each application package uses the standard ROS 2 layout: `package.xml`,
`setup.py`, the Python sources under `<package>/`, and tests under `test/`.
`greenhouse_bringup` is an `ament_cmake` package that installs the `launch/` and
`config/` directories.

## Nodes

| Node | Package | Subscribes | Publishes | Services |
| --- | --- | --- | --- | --- |
| `temperature_sensor` | `greenhouse_sensors` | – | `/temperature` | – |
| `humidity_sensor` | `greenhouse_sensors` | – | `/humidity` | – |
| `ventilation_controller` | `greenhouse_control` | `/temperature` | `/ventilation_state` | `/toggle_ventilation` (server) |
| `irrigation_controller` | `greenhouse_control` | `/humidity` | `/irrigation_state` | `/toggle_irrigation` (server) |
| `alert_system` | `greenhouse_monitor` | `/temperature` | – | `/toggle_ventilation` (client) |
| `data_logger` | `greenhouse_monitor` | `/temperature`, `/humidity` | – | – |

Node names differ from the executable names: for example,
`ros2 run greenhouse_sensors temperature_node` starts the node
`temperature_sensor`. The table lists node names.

## Topics

| Topic | Type | Description |
| --- | --- | --- |
| `/temperature` | `std_msgs/msg/Float32` | Air temperature in degrees Celsius. |
| `/humidity` | `std_msgs/msg/Float32` | Relative humidity as a percentage. |
| `/ventilation_state` | `std_msgs/msg/Bool` | Current ventilation actuator state. |
| `/irrigation_state` | `std_msgs/msg/Bool` | Current irrigation actuator state. |

All topics use the default QoS profile (reliable, depth 10) except the two
actuator state topics. `/ventilation_state` and `/irrigation_state` use a
reliable, transient-local, depth-1 profile so that a subscriber which connects
after the stack started immediately receives the current actuator state instead
of waiting for the next change.

## Services

| Service | Type | Description |
| --- | --- | --- |
| `/toggle_ventilation` | `example_interfaces/srv/SetBool` | Force ventilation on or off. |
| `/toggle_irrigation` | `example_interfaces/srv/SetBool` | Force irrigation on or off. |

A manual request overrides the automatic state; the hysteresis logic resumes
from the requested state on the next sensor reading.

## Parameters

Defaults are defined in `src/greenhouse_bringup/config/greenhouse_params.yaml`,
which the launch file loads. Each top-level key in that file is a node name.
Override a single value on the command line with
`--ros-args -p <name>:=<value>`.

| Node | Parameter | Default | Description |
| --- | --- | --- | --- |
| `temperature_sensor` | `publish_rate` | `1.0` | Publication rate in Hz. |
| | `set_point` | `20.0` | Mean simulated temperature (°C). |
| | `noise_stddev` | `2.0` | Standard deviation of the simulated noise. |
| | `min_valid` / `max_valid` | `-40.0` / `85.0` | Accepted temperature range. |
| `humidity_sensor` | `publish_rate` | `1.0` | Publication rate in Hz. |
| | `set_point` | `60.0` | Mean simulated humidity (%). |
| | `noise_stddev` | `5.0` | Standard deviation of the simulated noise. |
| | `min_valid` / `max_valid` | `0.0` / `100.0` | Accepted humidity range. |
| `ventilation_controller` | `lower_temperature` | `20.0` | Turn ventilation off below this value. |
| | `upper_temperature` | `25.0` | Turn ventilation on above this value. |
| | `min_valid_temperature` / `max_valid_temperature` | `-40.0` / `85.0` | Accepted input range. |
| `irrigation_controller` | `lower_humidity` | `40.0` | Start irrigation below this value. |
| | `upper_humidity` | `60.0` | Stop irrigation above this value. |
| | `min_valid_humidity` / `max_valid_humidity` | `0.0` / `100.0` | Accepted input range. |
| `alert_system` | `critical_temperature` | `30.0` | Temperature that triggers an alert. |
| | `alert_cooldown` | `10.0` | Minimum seconds between two alerts. |
| | `min_valid_temperature` / `max_valid_temperature` | `-40.0` / `85.0` | Accepted input range. |
| `data_logger` | `log_directory` | `''` | CSV output directory; empty disables file logging. |
| | `log_filename` | `greenhouse_log.csv` | CSV file name inside `log_directory`. |

## Requirements

- Ubuntu 22.04
- ROS 2 Humble (with `rosdep`)
- Python 3.10

Runtime dependencies (`rclpy`, `std_msgs`, `example_interfaces`, `launch_ros`)
are declared in the relevant `package.xml` files and resolved by `rosdep`.
Development tools are listed in [`requirements-dev.txt`](requirements-dev.txt).

## Installation

```bash
mkdir -p ~/smart_greenhouse_ws/src
cd ~/smart_greenhouse_ws/src
git clone https://github.com/imad-elghadaoui/smart_greenhouse.git
cd ~/smart_greenhouse_ws
rosdep install --from-paths src --ignore-src -r -y
```

## Build

```bash
cd ~/smart_greenhouse_ws
colcon build --symlink-install
source install/setup.bash
```

## Running

Start the whole stack with the default parameters:

```bash
ros2 launch greenhouse_bringup greenhouse.launch.py
```

Nodes can also be started individually, for example:

```bash
ros2 run greenhouse_sensors temperature_node
ros2 run greenhouse_control ventilation_node
```

## Examples

Inspect a sensor stream:

```bash
ros2 topic echo /temperature
```

Watch the ventilation actuator state:

```bash
ros2 topic echo /ventilation_state
```

Override an actuator manually:

```bash
ros2 service call /toggle_ventilation example_interfaces/srv/SetBool "{data: true}"
ros2 service call /toggle_irrigation example_interfaces/srv/SetBool "{data: true}"
```

Enable CSV logging:

```bash
ros2 run greenhouse_monitor data_logger_node --ros-args -p log_directory:=/tmp/greenhouse
```

## Testing

Build first, then run the test suite:

```bash
cd ~/smart_greenhouse_ws
colcon test
colcon test-result --verbose
```

The suite covers three levels:

- **Unit tests** for the decision logic and helpers, which do not need a running
  ROS graph. They can be run directly from a package directory:

  ```bash
  cd src/greenhouse_control && python3 -m pytest test
  ```

- **Node tests** that build the nodes and drive their callbacks; they require
  `rclpy` and are skipped automatically when it is not installed.
- **An end-to-end launch test** (`greenhouse_bringup`) that starts the whole
  stack with the real launch file and asserts that the sensor and state topics
  stream and that the `toggle_ventilation` / `toggle_irrigation` services drive
  the actuator state topics.

Each package also runs the `ament` linters through `colcon test`:
`ament_flake8`, `ament_pep257` and `ament_copyright` for the Python packages,
and `ament_copyright`, `ament_lint_cmake` and `ament_xmllint` for
`greenhouse_bringup`.

### Pre-commit hooks

The same style checks can be run before committing:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

The hooks (defined in [`.pre-commit-config.yaml`](.pre-commit-config.yaml))
check YAML syntax, trailing whitespace and file endings, and run `flake8`
(99-character line limit) and `pydocstyle` with the ROS 2 ignore list. They are
a fast subset of the full `ament` linters run by `colcon test`.

## Continuous integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and
pull request:

- a **lint** job that runs the pre-commit hooks on all files;
- a **build-and-test** job that installs the declared dependencies with
  `rosdep`, verifies them with `rosdep check`, then builds the workspace and
  runs the full `colcon` test suite (unit, node and launch tests) on ROS 2
  Humble.

## Design notes

- **Pure logic, thin nodes.** Threshold and validation logic lives in plain
  Python modules, so it is tested without ROS and reused across nodes.
- **Hysteresis instead of single thresholds.** Actuators switch on and off at
  different values, which prevents chattering around a set point.
- **Input validation.** Readings that are NaN, infinite or outside the
  configured range are ignored and logged (throttled) instead of being fed to
  the control logic.
- **Non-blocking service calls.** The alert system checks service availability
  without waiting and handles the response asynchronously, so it never blocks
  the executor.
- **State topics keep the last value.** Actuator state is published with a
  transient-local QoS profile, so a monitoring tool started after the stack
  immediately sees the current state instead of waiting for the next change.
- **Rate-limited alerts.** A cooldown prevents a persistent critical condition
  from flooding the log and the ventilation service.
- **Clean shutdown.** All nodes share a single `run_node` helper that handles
  Ctrl+C, external shutdown and unexpected exceptions, and releases resources
  in a `finally` block.
- **Parameters over constants.** Every threshold, rate and bound is a ROS 2
  parameter with a documented default.

## Known limitations

- The sensors publish simulated data; no physical hardware is read.
- Irrigation is driven by relative humidity because no soil-moisture sensor is
  modelled. A production system would use soil moisture.
- A single greenhouse is assumed; there is no multi-zone or multi-node support.
- Alerts are written to the ROS log and forwarded to the ventilation service;
  there is no external notification channel (email, SMS, MQTT).
- Only standard message and service types are used; no custom interfaces are
  defined.
- The nodes are plain `rclpy` processes. ROS 2 Humble cannot load Python nodes
  into a `component_container`, and `rclpy` does not expose intra-process
  communication, so no nodelet/composition is used (see below).

## Future work

- Add hardware backends (for example DHT22/SHT31 and a soil-moisture sensor)
  behind the existing sensor abstraction.
- Model actuators as managed lifecycle nodes with a deterministic startup
  order.
- Port the latency-sensitive nodes to C++ `rclcpp` components (or move to a
  distribution with Python composition support) to enable intra-process
  communication and reduce overhead as the stack grows.
- Persist samples to a database and expose a dashboard.
- Add diagnostic publishing and a watchdog for sensor timeouts.

## License

Released under the [Apache-2.0](LICENSE) license.
