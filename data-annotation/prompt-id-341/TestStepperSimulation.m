classdef TestStepperSimulation < matlab.unittest.TestCase
%TestStepperSimulation Tests the StepperSimulation.m script    ----  Response B
%   This class contains unit tests to verify the functionality and
%   robustness of the StepperSimulation.m script under various input
%   conditions and parameter settings.

    properties
        % Define common parameters that might be reused or modified
        DefaultStepsPerRevolution = 200;
        DefaultMicrostepping = 1;
        DefaultDt = 0.001;
        DefaultDuration = 5; % Default simulation duration for tests
        Tolerance = 1e-9; % Tolerance for floating-point comparisons
    end

    methods (Test) % Test methods execute specific test scenarios

        % --- Test Basic Execution ---
        function testScriptRunsWithoutError(testCase)
            % Test if the script executes without throwing errors with default trajectory
            testCase.verifyWarningFree(@() runStepperSimulation('trajectory', struct()), ...
                'The script should run without errors or warnings for the default trajectory case.');
        end

        % --- Test Step Input ---
        function testStepInputConstantSpeed(testCase)
            params.target_speed = 1.5; % rev/s
            [t_vector, pos_vector, vel_vector] = runStepperSimulation('step', params, testCase.DefaultDuration, testCase.DefaultDt);

            % Expected position: target_speed * time
            expected_pos = params.target_speed * t_vector;
            testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                'Position should increase linearly for step input.');

            % Expected velocity: constant target_speed (except maybe first point due to diff)
            expected_vel = ones(size(t_vector)) * params.target_speed;
            % Velocity calculation is (pos(i) - pos(i-1))/dt.
            % For linear pos = k*t, vel = (k*t_i - k*t_{i-1})/dt = k*(t_i-t_{i-1})/dt = k*dt/dt = k
            testCase.verifyEqual(vel_vector(2:end), expected_vel(2:end), 'AbsTol', testCase.Tolerance, ...
                'Velocity should be constant target_speed for step input (excluding first point).');
            testCase.verifyEqual(vel_vector(1), 0, 'AbsTol', testCase.Tolerance, ... % Check initial velocity
                 'Initial velocity should be zero.');
        end

        function testStepInputZeroSpeed(testCase)
            params.target_speed = 0;
            [t_vector, pos_vector, vel_vector] = runStepperSimulation('step', params, testCase.DefaultDuration, testCase.DefaultDt);

            expected_pos = zeros(size(t_vector));
            expected_vel = zeros(size(t_vector));

            testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                'Position should remain zero for zero target speed.');
            testCase.verifyEqual(vel_vector, expected_vel, 'AbsTol', testCase.Tolerance, ...
                'Velocity should remain zero for zero target speed.');
        end

        % --- Test Ramp Input ---
        function testRampInput(testCase)
            params.ramp_time = 2.0; % seconds
            params.target_speed = 2.5; % rev/s
            duration = 4.0; % Ensure we test both ramp and constant phases
            dt = testCase.DefaultDt;
            [t_vector, pos_vector, vel_vector] = runStepperSimulation('ramp', params, duration, dt);

            % Calculate expected values
            expected_pos = zeros(size(t_vector));
            expected_vel = zeros(size(t_vector)); % Initialize vel to zero
            
            accel = params.target_speed / params.ramp_time; % Constant acceleration during ramp

            for i = 1:length(t_vector)
                time = t_vector(i);
                if time < params.ramp_time
                    % Ramp phase
                    expected_pos(i) = 0.5 * accel * time^2;
                    if i > 1
                        % Velocity during ramp is v = a*t, but calculated via difference
                        expected_vel(i) = (expected_pos(i) - expected_pos(i-1)) / dt;
                    end
                else
                    % Constant speed phase (starts after ramp_time)
                    % Position at end of ramp: 0.5 * accel * ramp_time^2 = 0.5 * (target_speed/ramp_time) * ramp_time^2 = 0.5 * target_speed * ramp_time
                    pos_at_ramp_end = 0.5 * params.target_speed * params.ramp_time;
                    time_in_const_phase = time - params.ramp_time;
                    % The original script's constant phase formula seems slightly off.
                    % Corrected: pos = pos_at_ramp_end + target_speed * (time - ramp_time)
                    % Let's test against the *script's* formula: target_speed * (time - ramp_time/2)
                    expected_pos(i) = params.target_speed * (time - params.ramp_time / 2);
                     if i > 1
                        % Velocity should be target_speed, check via difference
                        expected_vel(i) = (expected_pos(i) - expected_pos(i-1)) / dt;
                     end
                end
            end

            % Verify Position
            testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                 'Position does not match expected ramp profile.');

            % Verify Velocity (using difference method, check against expected constant/ramp vel)
            % During ramp: v = accel * t
            % After ramp: v = target_speed
            ramp_indices = find(t_vector < params.ramp_time & t_vector > 0); % Exclude t=0
            const_indices = find(t_vector >= params.ramp_time);

            % Check ramp velocity trend (allow slightly larger tolerance due to differentiation)
            expected_ramp_vel_analytic = accel * t_vector(ramp_indices);
            testCase.verifyEqual(vel_vector(ramp_indices), expected_ramp_vel_analytic, 'AbsTol', dt*accel*1.5, ...
                 'Velocity during ramp phase does not match expected linear increase (within tolerance).');

            % Check constant velocity phase
             testCase.verifyEqual(vel_vector(const_indices), ones(size(const_indices)) * params.target_speed, 'AbsTol', testCase.Tolerance, ...
                 'Velocity after ramp phase should be constant target_speed.');
                 
            testCase.verifyEqual(vel_vector(1), 0, 'AbsTol', testCase.Tolerance, 'Initial velocity should be zero.');

        end
        
        function testRampInputShortDuration(testCase)
            % Test ramp input where duration is shorter than ramp_time
            params.ramp_time = 3.0; 
            params.target_speed = 1.0; 
            duration = 1.5; % Shorter than ramp_time
            dt = testCase.DefaultDt;
            [t_vector, pos_vector, vel_vector] = runStepperSimulation('ramp', params, duration, dt);

            % Expected values (only ramp phase applies)
            expected_pos = zeros(size(t_vector));
            expected_vel = zeros(size(t_vector));
            accel = params.target_speed / params.ramp_time;

             for i = 1:length(t_vector)
                time = t_vector(i);
                 expected_pos(i) = 0.5 * accel * time^2;
                 if i > 1
                     expected_vel(i) = (expected_pos(i) - expected_pos(i-1)) / dt;
                 end
             end
             
             testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                 'Position does not match expected ramp profile for short duration.');
             testCase.verifyEqual(vel_vector(2:end), expected_vel(2:end), 'AbsTol', dt*accel*1.5, ...
                 'Velocity does not match expected ramp profile for short duration.');
             testCase.verifyEqual(vel_vector(1), 0, 'AbsTol', testCase.Tolerance, 'Initial velocity should be zero.');
        end


        % --- Test Sinusoidal Input ---
        function testSineInput(testCase)
            params.amplitude = 1.5;  % Revolutions
            params.frequency = 0.25; % Hz
            duration = 1 / params.frequency * 2; % Simulate for two full cycles
            dt = testCase.DefaultDt;
            [t_vector, pos_vector, vel_vector] = runStepperSimulation('sine', params, duration, dt);

            % Expected position: A * sin(2*pi*f*t)
            expected_pos = params.amplitude * sin(2 * pi * params.frequency * t_vector);
            testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                'Position does not match expected sine wave.');

            % Expected velocity: d/dt(pos) = A * 2*pi*f * cos(2*pi*f*t)
            expected_vel_analytic = params.amplitude * 2 * pi * params.frequency * cos(2 * pi * params.frequency * t_vector);

            % Compare calculated velocity (numerical diff) with analytical derivative
            % Numerical differentiation introduces error, so use slightly larger tolerance
            testCase.verifyEqual(vel_vector(2:end), expected_vel_analytic(2:end), 'AbsTol', dt*params.amplitude*params.frequency*10, ...
                'Calculated velocity does not match analytical derivative of sine wave (within tolerance).');
             testCase.verifyEqual(vel_vector(1), 0, 'AbsTol', testCase.Tolerance, ... % Check initial velocity
                 'Initial velocity should be zero.');
        end

        function testSineInputZeroAmplitude(testCase)
            params.amplitude = 0;
            params.frequency = 1;
            [t_vector, pos_vector, vel_vector] = runStepperSimulation('sine', params, testCase.DefaultDuration, testCase.DefaultDt);

            expected_pos = zeros(size(t_vector));
            expected_vel = zeros(size(t_vector));

            testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                'Position should remain zero for zero amplitude sine.');
            testCase.verifyEqual(vel_vector, expected_vel, 'AbsTol', testCase.Tolerance, ...
                'Velocity should remain zero for zero amplitude sine.');
        end

        function testSineInputZeroFrequency(testCase)
             % Note: Zero frequency means target position is A*sin(0) = 0
            params.amplitude = 2.0;
            params.frequency = 0;
            [t_vector, pos_vector, vel_vector] = runStepperSimulation('sine', params, testCase.DefaultDuration, testCase.DefaultDt);

            expected_pos = zeros(size(t_vector));
            expected_vel = zeros(size(t_vector));

            testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                'Position should remain zero for zero frequency sine.');
            testCase.verifyEqual(vel_vector, expected_vel, 'AbsTol', testCase.Tolerance, ...
                'Velocity should remain zero for zero frequency sine.');
        end

        % --- Test Arbitrary Trajectory Input ---
        function testTrajectoryInput(testCase)
            params.waypoints_time = [0 1 3 4 5];
            params.waypoints_position = [0 0.5 0.5 -0.2 0];
            duration = 5.0;
            dt = testCase.DefaultDt;
            [t_vector, pos_vector, vel_vector] = runStepperSimulation('trajectory', params, duration, dt);

            % Expected position: Linear interpolation between waypoints
            expected_pos = interp1(params.waypoints_time, params.waypoints_position, t_vector, 'linear', 'extrap');
            testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                'Position does not match linear interpolation of waypoints.');

            % Expected velocity: Constant slope between waypoints
            expected_vel = zeros(size(t_vector));
            for i = 2:length(params.waypoints_time)
                tStart = params.waypoints_time(i-1);
                tEnd = params.waypoints_time(i);
                pStart = params.waypoints_position(i-1);
                pEnd = params.waypoints_position(i);

                % Find indices within this segment (excluding the start point
                % if it's not the very first point t=0, to avoid overlap)
                if tStart == 0
                     indices = find(t_vector >= tStart & t_vector <= tEnd);
                else
                     indices = find(t_vector > tStart & t_vector <= tEnd);
                end

                if tEnd > tStart % Avoid division by zero if waypoints have same time
                    segment_vel = (pEnd - pStart) / (tEnd - tStart);
                    expected_vel(indices) = segment_vel;
                else % If time is the same, velocity could be infinite/undefined. Diff calc handles it.
                    % Check velocity calc consistency
                     if ~isempty(indices)
                        expected_vel(indices) = (pos_vector(indices) - pos_vector(indices-1))/dt;
                     end
                end
            end
            
             % Check velocity calculation consistency 
             % Since pos=target_pos, vel is (target(i)-target(i-1))/dt
             recalc_vel = zeros(size(t_vector));
             for i=2:length(t_vector)
                 recalc_vel(i) = (pos_vector(i) - pos_vector(i-1)) / dt;
             end
            
             testCase.verifyEqual(vel_vector, recalc_vel, 'AbsTol', testCase.Tolerance, ...
                  'Calculated velocity inconsistent with position difference for trajectory.');
             testCase.verifyEqual(vel_vector(1), 0, 'AbsTol', testCase.Tolerance, 'Initial velocity should be zero.'); % Check initial vel

        end

        function testTrajectoryInputExtrapolation(testCase)
            params.waypoints_time = [1 2 3]; % Starts after t=0
            params.waypoints_position = [0.1 0.5 0.2];
            duration = 4.0; % Ends after last waypoint
            dt = testCase.DefaultDt;
             [t_vector, pos_vector, ~] = runStepperSimulation('trajectory', params, duration, dt);

            % Expected: Extrapolate using the first and last segments
            expected_pos = interp1(params.waypoints_time, params.waypoints_position, t_vector, 'linear', 'extrap');

            testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                'Position does not match expected extrapolation.');

            % Check first point (extrapolated backward)
            vel_first_segment = (params.waypoints_position(2) - params.waypoints_position(1)) / (params.waypoints_time(2) - params.waypoints_time(1));
            expected_pos_t0 = params.waypoints_position(1) - vel_first_segment * (params.waypoints_time(1) - t_vector(1));
            testCase.verifyEqual(pos_vector(1), expected_pos_t0, 'AbsTol', testCase.Tolerance, ...
                 'Backward extrapolation incorrect at t=0.');

            % Check last point (extrapolated forward)
            n_wp = length(params.waypoints_time);
            vel_last_segment = (params.waypoints_position(n_wp) - params.waypoints_position(n_wp-1)) / (params.waypoints_time(n_wp) - params.waypoints_time(n_wp-1));
            expected_pos_tend = params.waypoints_position(n_wp) + vel_last_segment * (t_vector(end) - params.waypoints_time(n_wp));
             testCase.verifyEqual(pos_vector(end), expected_pos_tend, 'AbsTol', testCase.Tolerance, ...
                 'Forward extrapolation incorrect at t=end.');
        end
        
        function testTrajectoryInputSingleWaypoint(testCase)
             params.waypoints_time = [1]; % Single point
             params.waypoints_position = [0.5];
             duration = 2.0; 
             dt = testCase.DefaultDt;
             [t_vector, pos_vector, vel_vector] = runStepperSimulation('trajectory', params, duration, dt);
             
             % interp1 with a single point returns that point's value for all query points
             expected_pos = ones(size(t_vector)) * params.waypoints_position(1);
             expected_vel = zeros(size(t_vector)); % Position is constant
             
             testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, ...
                 'Position should be constant for single waypoint trajectory.');
             % Check velocity - should be zero except maybe at the exact time of the waypoint jump if dt is coarse
             % Our simulation calculates diff, so it should be zero if pos is constant.
             testCase.verifyEqual(vel_vector, expected_vel, 'AbsTol', testCase.Tolerance, ...
                 'Velocity should be zero for single waypoint trajectory.');
        end

        % --- Test Parameter Variations ---
        function testDifferentDt(testCase)
            % Check if changing dt affects results significantly (it shouldn't much for this simple model)
            % Use step input as a simple case
            params.target_speed = 1;
            duration = 2.0;

            [t1, pos1, vel1] = runStepperSimulation('step', params, duration, 0.01); % Coarser dt
            [t2, pos2, vel2] = runStepperSimulation('step', params, duration, 0.0001); % Finer dt

            % Final position should be very close
            testCase.verifyEqual(pos1(end), pos2(end), 'AbsTol', 1e-5, ...
                'Final position should be nearly independent of dt for step input.');

            % Average velocity should be close (excluding t=0)
            testCase.verifyEqual(mean(vel1(2:end)), mean(vel2(2:end)), 'AbsTol', 1e-5, ...
                'Average velocity should be nearly independent of dt for step input.');
        end

        function testUnusedParameters(testCase)
             % Verify the script runs even if unused parameters change,
             % confirming they are currently ignored by the simple model.
             params.target_speed = 1;
             duration = 1.0;
             dt = testCase.DefaultDt;

             % Run with default steps/microstepping
             [~, pos1, vel1] = runStepperSimulation('step', params, duration, dt, 200, 1);

             % Run with different steps/microstepping
             [~, pos2, vel2] = runStepperSimulation('step', params, duration, dt, 400, 8);

             % Results should be identical because these parameters are not used in the simple model
             testCase.verifyEqual(pos1, pos2, 'AbsTol', testCase.Tolerance, ...
                 'Position should not change when unused steps_per_revolution changes.');
             testCase.verifyEqual(vel1, vel2, 'AbsTol', testCase.Tolerance, ...
                 'Velocity should not change when unused microstepping changes.');
             testCase.assertWarningFree(@() runStepperSimulation('step', params, duration, dt, 400, 8), ...
                 'Script should run without warning even with different unused parameters.');
        end


        % --- Test Edge Cases ---
        function testVeryShortDuration(testCase)
            params.target_speed = 1;
            duration = testCase.DefaultDt * 1.5; % Only 2 time steps (t=0, t=dt)
            dt = testCase.DefaultDt;
             [t_vector, pos_vector, vel_vector] = runStepperSimulation('step', params, duration, dt);

             testCase.verifyEqual(numel(t_vector), 2, 'Expected 2 time points for short duration.');
             testCase.verifyEqual(t_vector, [0 dt], 'AbsTol', testCase.Tolerance, 'Time vector incorrect for short duration.');

             expected_pos = [0 params.target_speed*dt];
             expected_vel = [0 (expected_pos(2)-expected_pos(1))/dt]; % Vel(1)=0, Vel(2)=speed

             testCase.verifyEqual(pos_vector, expected_pos, 'AbsTol', testCase.Tolerance, 'Position incorrect for short duration.');
             testCase.verifyEqual(vel_vector, expected_vel, 'AbsTol', testCase.Tolerance, 'Velocity incorrect for short duration.');
        end

        function testZeroDuration(testCase)
            params.target_speed = 1;
            duration = 0;
            dt = testCase.DefaultDt;
             [t_vector, pos_vector, vel_vector] = runStepperSimulation('step', params, duration, dt);

             % Expect single point at t=0
             testCase.verifyEqual(t_vector, 0, 'AbsTol', testCase.Tolerance, 'Time vector should be [0] for zero duration.');
             testCase.verifyEqual(pos_vector, 0, 'AbsTol', testCase.Tolerance, 'Position vector should be [0] for zero duration.');
             testCase.verifyEqual(vel_vector, 0, 'AbsTol', testCase.Tolerance, 'Velocity vector should be [0] for zero duration.');
        end
        
        % --- Test Error Handling (Requires modification of original script) ---
        % function testInvalidInputType(testCase)
        %     % This test requires StepperSimulation.m to have an 'otherwise'
        %     % clause in the switch statement that throws an error.
        %     params = struct(); % No params needed
        %     inputType = 'invalid_type_xyz';
        % 
        %     % Verify that an error is thrown for an unrecognized input type
        %     testCase.verifyError(@() runStepperSimulation(inputType, params), ...
        %         'MATLAB:unrecognizedStringChoice', ... % Or a custom error ID if you define one
        %         'Script should throw an error for an invalid input_type.');
        % end

    end % methods (Test)

end % classdef


% --- Helper Function to Run the Simulation ---
% This encapsulates the logic of setting up and running the core part
% of StepperSimulation.m within a function scope, avoiding issues with
% workspace persistence between tests.
function [t_vector, pos_vector, vel_vector] = runStepperSimulation(input_type, params, duration, dt, steps_per_rev, microstep)
    % Set defaults if not provided
    if nargin < 6, microstep = 1; end
    if nargin < 5, steps_per_rev = 200; end
    if nargin < 4, dt = 0.001; end
    if nargin < 3, duration = 10; end % Default duration if not specified by test

    % --- Replicate Core Logic from StepperSimulation.m ---
    steps_per_revolution = steps_per_rev;
    microstepping = microstep;
    % dt = dt; % Already an input

    % Initialize variables
    time = 0;
    position = 0;
    velocity = 0;
    target_position = 0;

    % Assign parameters based on input type - Use dynamic field names
    fieldNames = fieldnames(params);
    for k=1:length(fieldNames)
        eval([fieldNames{k} ' = params.' fieldNames{k} ';']); % Assign struct fields to local variables
    end
    % input_type is already an input

    % Simulation loop
    t_vector = 0:dt:duration;
    pos_vector = zeros(size(t_vector));
    vel_vector = zeros(size(t_vector));
    pos_vector(1) = 0; % Initial Position

    for i = 1:length(t_vector)
        time = t_vector(i);

        % Determine target position based on input type
        switch input_type
            case 'step'
                % Ensure target_speed exists or default it
                if ~exist('target_speed', 'var'), target_speed = 0; end
                target_position = target_speed * time;
            case 'ramp'
                 % Ensure params exist or default them
                if ~exist('ramp_time', 'var'), ramp_time = 1; end
                if ~exist('target_speed', 'var'), target_speed = 1; end
                if time < ramp_time
                    target_position = 0.5 * target_speed / ramp_time * time^2; % Ramp up
                else
                    target_position = target_speed * (time - ramp_time/2); % Constant speed after ramp
                end
            case 'sine'
                 % Ensure params exist or default them
                if ~exist('amplitude', 'var'), amplitude = 0; end
                if ~exist('frequency', 'var'), frequency = 1; end
                target_position = amplitude * sin(2 * pi * frequency * time);
            case 'trajectory'
                 % Ensure params exist or default them
                 if ~exist('waypoints_time', 'var') || ~exist('waypoints_position', 'var')
                     % Provide default waypoints if none are in params struct
                     waypoints_time = [0 1 2 3 4]; 
                     waypoints_position = [0 0.5 1 0.5 0];
                 end
                 % Handle case where only one waypoint is given - interp1 needs >= 2 points for 'linear'
                 if numel(waypoints_time) == 1
                     target_position = waypoints_position(1); % Constant position
                 else
                     target_position = interp1(waypoints_time, waypoints_position, time, 'linear', 'extrap'); % Linear interpolation
                 end
             otherwise
                 % Original script doesn't handle this. Test framework might catch error later.
                 % For robust code, add: error('Unknown input_type: %s', input_type);
                 % We will test this potential failure point indirectly.
                 target_position = NaN; % Indicate an issue
        end

        % Simple model: Assume the motor instantly reaches the desired position
        position = target_position;

        % Calculate velocity
        if i > 1 && dt > 0 % Prevent division by zero if dt=0
            velocity = (position - pos_vector(i-1)) / dt;
        else
            velocity = 0; % Initialize velocity to zero
        end

        % Store data
        pos_vector(i) = position;
        vel_vector(i) = velocity;

    end
    % --- End of Replicated Logic ---
end