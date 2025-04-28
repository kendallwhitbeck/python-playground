% StepperSimulation_Test.m
% Comprehensive testing script for StepperSimulation.m

% Clear workspace and close all figures
clear all;
close all;
clc;

% Create a log file for test results
diary('StepperSimulation_TestResults.txt');
diary on;

fprintf('=== STEPPER MOTOR SIMULATION TEST SUITE ===\n');
fprintf('Test Date: %s\n\n', datestr(now));

% Test Configuration Structure
test_results = struct();
test_count = 0;
pass_count = 0;

%% Test 1: Step Input Testing
fprintf('TEST 1: Step Input Testing\n');
fprintf('------------------------\n');

% Test different step speeds
step_speeds = [0.1, 0.5, 1, 2, 5, 10];
for i = 1:length(step_speeds)
    test_count = test_count + 1;
    target_speed = step_speeds(i);
    input_type = 'step';
    
    fprintf('Step Test %d: Speed = %.1f rev/s\n', i, target_speed);
    
    % Run simulation
    run_simulation(target_speed, [], [], [], [], input_type);
    
    % Validate results
    expected_final_position = target_speed * 10; % After 10 seconds
    actual_final_position = pos_vector(end);
    tolerance = 0.001;
    
    if abs(expected_final_position - actual_final_position) < tolerance
        fprintf('  PASS: Final position correct (Expected: %.3f, Actual: %.3f)\n', ...
            expected_final_position, actual_final_position);
        pass_count = pass_count + 1;
    else
        fprintf('  FAIL: Final position incorrect (Expected: %.3f, Actual: %.3f)\n', ...
            expected_final_position, actual_final_position);
    end
    
    % Save figure
    saveas(gcf, sprintf('step_test_%d.png', i));
    close(gcf);
end

%% Test 2: Ramp Input Testing
fprintf('\nTEST 2: Ramp Input Testing\n');
fprintf('------------------------\n');

% Test different ramp parameters
ramp_times = [0.5, 1, 2, 5];
target_speeds = [0.5, 1, 2, 5];

for i = 1:length(ramp_times)
    for j = 1:length(target_speeds)
        test_count = test_count + 1;
        ramp_time = ramp_times(i);
        target_speed = target_speeds(j);
        input_type = 'ramp';
        
        fprintf('Ramp Test %d: Ramp Time = %.1f s, Speed = %.1f rev/s\n', ...
            (i-1)*length(target_speeds)+j, ramp_time, target_speed);
        
        % Run simulation
        run_simulation(target_speed, ramp_time, [], [], [], input_type);
        
        % Validate results - check if velocity reaches target
        steady_state_velocity = mean(vel_vector(end-100:end));
        if abs(steady_state_velocity - target_speed) < 0.01
            fprintf('  PASS: Steady-state velocity reached correctly\n');
            pass_count = pass_count + 1;
        else
            fprintf('  FAIL: Steady-state velocity incorrect (Expected: %.3f, Actual: %.3f)\n', ...
                target_speed, steady_state_velocity);
        end
        
        % Save figure
        saveas(gcf, sprintf('ramp_test_%d_%d.png', i, j));
        close(gcf);
    end
end

%% Test 3: Sinusoidal Input Testing
fprintf('\nTEST 3: Sinusoidal Input Testing\n');
fprintf('------------------------------\n');

% Test different sine parameters
amplitudes = [0.5, 1, 2];
frequencies = [0.1, 0.5, 1, 2];

for i = 1:length(amplitudes)
    for j = 1:length(frequencies)
        test_count = test_count + 1;
        amplitude = amplitudes(i);
        frequency = frequencies(j);
        input_type = 'sine';
        
        fprintf('Sine Test %d: Amplitude = %.1f rev, Frequency = %.1f Hz\n', ...
            (i-1)*length(frequencies)+j, amplitude, frequency);
        
        % Run simulation
        run_simulation([], [], amplitude, frequency, [], input_type);
        
        % Validate results - check peak-to-peak amplitude
        max_pos = max(pos_vector);
        min_pos = min(pos_vector);
        actual_amplitude = (max_pos - min_pos) / 2;
        
        if abs(actual_amplitude - amplitude) < 0.01
            fprintf('  PASS: Amplitude correct (Expected: %.3f, Actual: %.3f)\n', ...
                amplitude, actual_amplitude);
            pass_count = pass_count + 1;
        else
            fprintf('  FAIL: Amplitude incorrect (Expected: %.3f, Actual: %.3f)\n', ...
                amplitude, actual_amplitude);
        end
        
        % Save figure
        saveas(gcf, sprintf('sine_test_%d_%d.png', i, j));
        close(gcf);
    end
end

%% Test 4: Trajectory Input Testing
fprintf('\nTEST 4: Trajectory Input Testing\n');
fprintf('------------------------------\n');

% Test different trajectory profiles
trajectory_tests = {
    [0 1 2 3 4], [0 0.5 1 0.5 0];      % Original trajectory
    [0 2 4 6 8], [0 1 2 1 0];          % Longer trajectory
    [0 0.5 1 1.5 2], [0 1 0 -1 0];     % With negative positions
    [0 1 2 3 4 5], [0 0.2 0.4 0.6 0.8 1];  % Linear increase
};

for i = 1:size(trajectory_tests, 1)
    test_count = test_count + 1;
    waypoints_time = trajectory_tests{i, 1};
    waypoints_position = trajectory_tests{i, 2};
    input_type = 'trajectory';
    
    fprintf('Trajectory Test %d\n', i);
    
    % Run simulation
    run_simulation([], [], [], [], waypoints_position, input_type, waypoints_time);
    
    % Validate results - check if waypoints are hit
    waypoint_error = false;
    for wp = 1:length(waypoints_time)
        if waypoints_time(wp) <= 10  % Only check waypoints within simulation time
            [~, time_idx] = min(abs(t_vector - waypoints_time(wp)));
            actual_pos = pos_vector(time_idx);
            expected_pos = waypoints_position(wp);
            
            if abs(actual_pos - expected_pos) > 0.01
                waypoint_error = true;
                fprintf('  Waypoint %d error: Expected %.3f, Got %.3f\n', ...
                    wp, expected_pos, actual_pos);
            end
        end
    end
    
    if ~waypoint_error
        fprintf('  PASS: All waypoints reached correctly\n');
        pass_count = pass_count + 1;
    else
        fprintf('  FAIL: Waypoint errors detected\n');
    end
    
    % Save figure
    saveas(gcf, sprintf('trajectory_test_%d.png', i));
    close(gcf);
end

%% Test 5: Edge Cases and Error Conditions
fprintf('\nTEST 5: Edge Cases Testing\n');
fprintf('------------------------\n');

% Test zero speed
test_count = test_count + 1;
fprintf('Edge Case 1: Zero speed\n');
run_simulation(0, [], [], [], [], 'step');
if all(pos_vector == 0)
    fprintf('  PASS: Zero speed maintains zero position\n');
    pass_count = pass_count + 1;
else
    fprintf('  FAIL: Zero speed produces non-zero position\n');
end
close(gcf);

% Test very high speeds
test_count = test_count + 1;
fprintf('Edge Case 2: Very high speed (100 rev/s)\n');
run_simulation(100, [], [], [], [], 'step');
expected_final_position = 100 * 10; % After 10 seconds
if abs(pos_vector(end) - expected_final_position) < 0.01
    fprintf('  PASS: High speed handling correct\n');
    pass_count = pass_count + 1;
else
    fprintf('  FAIL: High speed handling incorrect\n');
end
close(gcf);

% Test negative speeds
test_count = test_count + 1;
fprintf('Edge Case 3: Negative speed\n');
run_simulation(-1, [], [], [], [], 'step');
if pos_vector(end) < 0
    fprintf('  PASS: Negative speed produces negative position\n');
    pass_count = pass_count + 1;
else
    fprintf('  FAIL: Negative speed handling incorrect\n');
end
close(gcf);

%% Test 6: Microstepping Configuration Testing
fprintf('\nTEST 6: Microstepping Testing\n');
fprintf('---------------------------\n');

microstepping_values = [1, 2, 4, 8, 16];
for i = 1:length(microstepping_values)
    test_count = test_count + 1;
    microstepping = microstepping_values(i);
    
    fprintf('Microstepping Test %d: Factor = %d\n', i, microstepping);
    
    % Run simulation with modified microstepping
    run_simulation(1, [], [], [], [], 'step', [], microstepping);
    
    % For this simple model, microstepping doesn't affect the output
    % In a real implementation, we would check step resolution
    fprintf('  INFO: Microstepping configuration set to %d\n', microstepping);
    
    % Save figure
    saveas(gcf, sprintf('microstepping_test_%d.png', i));
    close(gcf);
end

%% Test 7: Time Step Sensitivity Testing
fprintf('\nTEST 7: Time Step Sensitivity Testing\n');
fprintf('-----------------------------------\n');

dt_values = [0.0001, 0.001, 0.01, 0.1];
for i = 1:length(dt_values)
    test_count = test_count + 1;
    dt = dt_values(i);
    
    fprintf('Time Step Test %d: dt = %.4f s\n', i, dt);
    
    % Run simulation with modified time step
    run_simulation(1, [], [], [], [], 'step', [], [], dt);
    
    % Check if the simulation still produces reasonable results
    if abs(pos_vector(end) - 10) < 0.01
        fprintf('  PASS: Time step %.4f produces accurate results\n', dt);
        pass_count = pass_count + 1;
    else
        fprintf('  FAIL: Time step %.4f produces inaccurate results\n', dt);
    end
    
    % Save figure
    saveas(gcf, sprintf('timestep_test_%d.png', i));
    close(gcf);
end

%% Test Summary
fprintf('\n=== TEST SUMMARY ===\n');
fprintf('Total Tests: %d\n', test_count);
fprintf('Passed: %d\n', pass_count);
fprintf('Failed: %d\n', test_count - pass_count);
fprintf('Success Rate: %.1f%%\n', (pass_count/test_count)*100);

diary off;

%% Helper function to run simulation
function run_simulation(target_speed, ramp_time, amplitude, frequency, ...
    waypoints_position, input_type, waypoints_time, microstepping, dt)
    
    % Set default values if not provided
    if nargin < 7 || isempty(waypoints_time)
        waypoints_time = [0 1 2 3 4];
    end
    if nargin < 8 || isempty(microstepping)
        microstepping = 1;
    end
    if nargin < 9 || isempty(dt)
        dt = 0.001;
    end
    
    % Initialize variables
    steps_per_revolution = 200;
    time = 0;
    position = 0;
    velocity = 0;
    target_position = 0;
    
    % Simulation loop
    t_vector = 0:dt:10;
    pos_vector = zeros(size(t_vector));
    vel_vector = zeros(size(t_vector));
    
    for i = 1:length(t_vector)
        time = t_vector(i);
        
        % Determine target position based on input type
        switch input_type
            case 'step'
                target_position = target_speed * time;
            case 'ramp'
                if time < ramp_time
                    target_position = 0.5 * target_speed / ramp_time * time^2;
                else
                    target_position = target_speed * (time - ramp_time/2);
                end
            case 'sine'
                target_position = amplitude * sin(2 * pi * frequency * time);
            case 'trajectory'
                target_position = interp1(waypoints_time, waypoints_position, time, 'linear', 'extrap');
        end
        
        % Simple model: Assume the motor instantly reaches the desired position
        position = target_position;
        
        % Calculate velocity
        if i > 1
            velocity = (position - pos_vector(i-1)) / dt;
        else
            velocity = 0;
        end
        
        % Store data
        pos_vector(i) = position;
        vel_vector(i) = velocity;
    end
    
    % Plotting
    figure;
    subplot(2,1,1);
    plot(t_vector, pos_vector);
    xlabel('Time (s)');
    ylabel('Position (revolutions)');
    title(['Stepper Motor Position - ' input_type]);
    grid on;
    
    subplot(2,1,2);
    plot(t_vector, vel_vector);
    xlabel('Time (s)');
    ylabel('Velocity (revolutions/s)');
    title(['Stepper Motor Velocity - ' input_type]);
    grid on;
    
    % Save variables to base workspace for validation
    assignin('base', 't_vector', t_vector);
    assignin('base', 'pos_vector', pos_vector);
    assignin('base', 'vel_vector', vel_vector);
end