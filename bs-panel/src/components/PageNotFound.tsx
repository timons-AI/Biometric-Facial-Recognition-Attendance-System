import React from "react";
import { Callout, Intent } from "@blueprintjs/core";

const PageNotFound: React.FC = () => {
  return (
    <Callout intent={Intent.DANGER} title="Page Not Found" className="mt-4">
      Oops! The page you are looking for does not exist.
    </Callout>
  );
};

export default PageNotFound;
