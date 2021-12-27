from mip import Model, CONTINUOUS, INTEGER
import math


def create_model_for_image(img):
    rows, cols = img.shape
    m = Model("img-model")

    # TODO: Pad rows, cols to a power of 2.
    nr_square_levels = round(min(math.log(cols, 2), math.log(rows, 2))) + 1

    square_variables = []
    abs_value_variables = []
    # TODO: Populate a feasible_solution = []. Format seems to be a list of tuples as (VAR, VALUE).

    for i in range(0, nr_square_levels):
        upper_bound = 64
        lower_bound = -63
        if i == 0:
            upper_bound = 127
            lower_bound = -128

        vars_shape = (round(cols / (2 ** i)), round(rows / (2 ** i)))

        # Variables which represent squares on level i
        square_variables.append(m.add_var_tensor(
            vars_shape,
            name=str(i),
            var_type=INTEGER,
            ub=upper_bound,
            lb=lower_bound
        ))

        # Helper variables to allow us to minimize the sum of the absolute values of the above variables.
        abs_value_variables.append(m.add_var_tensor(
            vars_shape,
            name=str(i) + "_abs_helpers",
            var_type=CONTINUOUS,
            ub=upper_bound,
            lb=lower_bound,
            obj=1
        ))

    # Constraints to allow us to minimize a sum of absolute values
    # https://math.stackexchange.com/questions/623568/minimizing-the-sum-of-absolute-values-with-a-linear-solver/623569
    for i in range(0, nr_square_levels):
        for square_var, abs_helper in zip(square_variables[i].flatten(), abs_value_variables[i].flatten()):
            m += square_var <= abs_helper
            m += square_var >= -abs_helper

    # Constraints which force the squares to be an encoding of the image.
    for x in range(0, cols):
        for y in range(0, rows):
            variables_xy = []
            for i in range(nr_square_levels):
                x_square = x // (2 ** i)
                y_square = y // (2 ** i)
                variables_xy.append(square_variables[i][x_square][y_square])

            # Center image values around -128 to 127. 
            m.add_constr(sum(variables_xy) == img[x][y] - 128)

            continue

    return m
