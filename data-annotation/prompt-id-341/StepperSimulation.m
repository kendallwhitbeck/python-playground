steps_per_revolution = 200;  % Number of steps for one full rotation
microstepping = 1;          % Microstepping factor (e.g., 1, 2, 4, 8...)
dt = 0.001;                % Time step for simulation

% Initialize variables
time = 0;
position = 0; % in revolutions
velocity = 0; % in revolutions per second
target_position = 0; % in revolutions

% Input conditions (Many different types of inputs possible)

% 1. Step Input (Constant speed)
% target_speed = 1; % revolutions per second
% input_type = 'step';

% 2. Ramp Input (Accelerating then constant speed)
% ramp_time = 2; % seconds
% target_speed = 2; % revolutions per second
% input_type = 'ramp';

% 3. Sinusoidal Input (Oscillating motion)
% amplitude = 1;  % Revolutions
% frequency = 0.5; % Hz
% input_type = 'sine';

% 4. Arbitrary Trajectory Input (Define waypoints) - Example
 waypoints_time = [0 1 2 3 4]; % Time at each waypoint
 waypoints_position = [0 0.5 1 0.5 0]; % Position at each waypoint
 input_type = 'trajectory';


% Simulation loop
t_vector = 0:dt:10;  % Create the time vector first
pos_vector = zeros(size(t_vector)); % Pre-allocate position vector
vel_vector = zeros(size(t_vector)); % Pre-allocate velocity vector

pos_vector(1) = 0; % Initial Position

for i = 1:length(t_vector)
    time = t_vector(i);

    % Determine target position based on input type
    switch input_type
        case 'step'
            target_position = target_speed * time;
        case 'ramp'
            if time < ramp_time
                target_position = 0.5 * target_speed / ramp_time * time^2; % Ramp up
            else
                target_position = target_speed * (time - ramp_time/2); % Constant speed after ramp
            end
        case 'sine'
            target_position = amplitude * sin(2 * pi * frequency * time);
        case 'trajectory'
            target_position = interp1(waypoints_time, waypoints_position, time, 'linear', 'extrap'); % Linear interpolation
    end

    % Simple model: Assume the motor instantly reaches the desired position
    position = target_position;

    % Calculate velocity
    if i > 1  % Only calculate velocity after the first time step
        velocity = (position - pos_vector(i-1)) / dt; 
    else
        velocity = 0; % Initialize velocity to zero
    end

    % Store data for plotting
    pos_vector(i) = position;
    vel_vector(i) = velocity;

end

% Plotting
figure;

subplot(2,1,1);
plot(t_vector, pos_vector);
xlabel('Time (s)');
ylabel('Position (revolutions)');
title('Stepper Motor Position');
grid on;

subplot(2,1,2);
plot(t_vector, vel_vector);
xlabel('Time (s)');
ylabel('Velocity (revolutions/s)');
title('Stepper Motor Velocity');
grid on;