var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};


dagcomponentfuncs.CustomTooltipGraph = function (props) {
    return React.createElement(
        window.dash_core_components.Graph, {
            figure: props.value,
        })
};